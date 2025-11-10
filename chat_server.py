import os
import socket
import threading
import argparse
import time


HOST = os.getenv("HOST", "0.0.0.0")
DEFAULT_PORT = int(os.getenv("CHAT_PORT", 4000))
IDLE_TIMEOUT = int(os.getenv("CHAT_IDLE_TIMEOUT", 60))


lock = threading.Lock()


class Client:
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.username = None
        self.buffer = b""
        self.last_active = time.time()
        self.lock = threading.Lock()

    def send(self, text: str):
        try:
            with self.lock:
                if not text.endswith("\n"):
                    text += "\n"
                self.conn.sendall(text.encode("utf-8"))
        except Exception:
            pass


clients = {}
conns = set()


def broadcast(text: str, exclude=None):
    with lock:
        for c in list(conns):
            if c.username and c is not exclude:
                c.send(text)


def handle_login(line: str, client: Client):
    parts = line.strip().split(None, 1)
    if len(parts) != 2:
        client.send("ERR invalid-login-format")
        return False
    username = parts[1].strip()
    if not username:
        client.send("ERR invalid-username")
        return False
    with lock:
        if username in clients:
            client.send("ERR username-taken")
            return False
        clients[username] = client
        client.username = username
    client.send("OK")
    broadcast(f"INFO {username} connected", exclude=client)
    return True


def handle_msg(line: str, client: Client):
    parts = line.split(None, 1)
    if len(parts) < 2:
        return
    text = parts[1].strip()
    broadcast(f"MSG {client.username} {text}")


def handle_dm(line: str, client: Client):
    parts = line.split(None, 2)
    if len(parts) < 3:
        client.send("ERR dm-format")
        return
    target = parts[1]
    text = parts[2]
    with lock:
        target_client = clients.get(target)
    if not target_client:
        client.send("ERR user-not-found")
        return
    target_client.send(f"DM {client.username} {text}")
    client.send(f"DM {client.username} {text}")


def handle_who(client: Client):
    with lock:
        for uname in clients:
            client.send(f"USER {uname}")


def handle_ping(client: Client):
    client.send("PONG")


def remove_client(client: Client):
    with lock:
        if client in conns:
            conns.remove(client)
        if client.username and clients.get(client.username) is client:
            del clients[client.username]
            broadcast(f"INFO {client.username} disconnected", exclude=client)
    try:
        client.conn.close()
    except Exception:
        pass


def client_thread(conn, addr):
    client = Client(conn, addr)
    conns.add(client)
    conn.settimeout(1.0)
    logged_in = False
    client.send("Welcome! Please LOGIN <username>")
    try:
        while True:
            try:
                data = conn.recv(4096)
            except socket.timeout:
                if time.time() - client.last_active > IDLE_TIMEOUT:
                    client.send("ERR idle-timeout")
                    break
                continue
            except Exception:
                break
            if not data:
                break
            client.last_active = time.time()
            client.buffer += data
            while b"\n" in client.buffer:
                line, client.buffer = client.buffer.split(b"\n", 1)
                line = line.decode().strip()
                if not line:
                    continue
                if not logged_in:
                    if line.upper().startswith("LOGIN "):
                        logged_in = handle_login(line, client)
                    else:
                        client.send("ERR please-login-first")
                else:
                    if line.upper().startswith("MSG "):
                        handle_msg(line, client)
                    elif line.upper() == "WHO":
                        handle_who(client)
                    elif line.upper().startswith("DM "):
                        handle_dm(line, client)
                    elif line.upper() == "PING":
                        handle_ping(client)
                    else:
                        client.send("ERR unknown-command")
    finally:
        remove_client(client)


def main():
    global IDLE_TIMEOUT

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--idle-timeout", type=int, default=IDLE_TIMEOUT)
    args = parser.parse_args()

    IDLE_TIMEOUT = args.idle_timeout

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((HOST, args.port))
    server_sock.listen(10)
    print(f"Server running on {HOST}:{args.port} (timeout={IDLE_TIMEOUT}s)")

    while True:
        conn, addr = server_sock.accept()
        threading.Thread(target=client_thread, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    main()
