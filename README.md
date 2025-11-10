# Simple Socket Chat Server

### Overview
A multi-user TCP chat server using Python sockets and threads.  
Implements:
- LOGIN <username>
- MSG <text>
- WHO
- DM <username> <text>
- PING → PONG
- Idle timeout + disconnect notifications

---

## ⚙️ Setup

1. Install Python 3.8+  
2. Clone or copy this project:
```bash
   git clone <your-repo> socket-chat
   cd socket-chat
```
3. Run the server 
```bash  
python3 chat_server.py  
```
4. Connect two or more clients using either of the two ways:  
A. Netcat:
```bash 
nc localhost 4000
LOGIN Alice
MSG Hello everyone!  
```
B. Python client:  
```bash  
python3 chat_client.py --host 127.0.0.1 --port 4000  
```

--- 

## 🧠 Example Session
Client 1: 
```bash
LOGIN ashutosh
OK
MSG hello everyone...how are all of you?  
```

Client 2:  
```bash  
LOGIN shristi
OK
MSG hey ashutosh!
```  

---

## 🧪 Optional Commands  

| **Command** | **Description** |
|--------------|-----------------|
| `WHO` | Lists active users |
| `DM <username> <text>` | Sends a private message to the specified user |
| `PING` | Replies with `PONG` |
| `ERR` | Returned on invalid input |
| `INFO <username> disconnected` | Shown when someone leaves the chat |

--- 

## 🧰 Demo Video
Watch the working demo here: [Demo](https://www.loom.com/share/4e5f452cebf84f07b485b3a88ac0f7b9)

