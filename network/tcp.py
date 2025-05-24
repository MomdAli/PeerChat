import socket
from typing import Tuple

def recv_all(conn: socket.socket, length: int) -> bytes:
    data = b''
    while len(data) < length:
        more = conn.recv(length - len(data))
        if not more:
            raise ConnectionError("Connection closed before message complete")
        data += more
    return data

def recv_message(conn: socket.socket) -> str:
    raw_len = recv_all(conn, 10)
    msglen = int(raw_len.decode().strip())
    return recv_all(conn, msglen).decode()

def send_message(conn: socket.socket, msg: str):
    msg = msg.encode()
    msg_len = f"{len(msg):<10}".encode()  # length prefix (10 bytes)
    conn.sendall(msg_len + msg)