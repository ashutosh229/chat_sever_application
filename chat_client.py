import socket
import threading
import argparse
import sys


sys.stdout.reconfigure(line_buffering=True)


def receive_messages(sock):
    while True:
        try:
            data = sock.recv(4096)
            if not data:
                break
            print(data.decode().strip())
        except Exception:
            break


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=4000)
    args = parser.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((args.host, args.port))

    threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()

    print(
        "Connected. Type commands like LOGIN <name>, MSG <text>, WHO, DM <user> <text>, PING"
    )
    try:
        while True:
            msg = input()
            if not msg:
                continue
            sock.sendall((msg + "\n").encode())
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        sock.close()


if __name__ == "__main__":
    main()
