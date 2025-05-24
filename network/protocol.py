"""
Protocol message formats and parsing utilities for PeerChat.
"""

# --- Client-Server Protocol ---
def parse_register(msg: str):
    parts = msg.strip().split()
    return (parts[1], int(parts[2])) if len(parts) == 3 and parts[0] == "REGISTER" else None

def make_joined(nickname: str, ip: str, udp_port: int) -> str:
    return f"JOINED {nickname} {ip} {udp_port}"

def make_left(nickname: str) -> str:
    return f"LEFT {nickname}"

def make_broadcast(message: str) -> str:
    return f"BROADCAST {message}"

def parse_port(msg: str):
    parts = msg.strip().split()
    return (parts[1], int(parts[2])) if len(parts) == 3 and parts[0] == "PORT" else None

def make_port(nickname: str, tcp_port: int) -> str:
    return f"PORT {nickname} {tcp_port}"

# --- Peer-to-Peer Protocol ---
def make_chat_request(nickname: str) -> str:
    return f"CHAT_REQUEST {nickname}"

def is_chat_request(msg: str):
    return msg.startswith("CHAT_REQUEST ")

def parse_chat_request(msg: str):
    parts = msg.strip().split()
    return parts[1] if len(parts) == 2 and parts[0] == "CHAT_REQUEST" else None

def make_chat_accept(nickname: str) -> str:
    return f"CHAT_ACCEPT {nickname}"

def is_chat_accept(msg: str):
    return msg.startswith("CHAT_ACCEPT ")

def parse_chat_accept(msg: str):
    parts = msg.strip().split()
    return parts[1] if len(parts) == 2 and parts[0] == "CHAT_ACCEPT" else None

def make_chat_reject(nickname: str) -> str:
    return f"CHAT_REJECT {nickname}"

def is_chat_reject(msg: str):
    return msg.startswith("CHAT_REJECT ")

def parse_chat_reject(msg: str):
    parts = msg.strip().split()
    return parts[1] if len(parts) == 2 and parts[0] == "CHAT_REJECT" else None

def make_left_chat(nickname: str) -> str:
    return f"LEFT_CHAT {nickname}"

def is_left_chat(msg: str):
    return msg.startswith("LEFT_CHAT ")

def parse_left_chat(msg: str):
    parts = msg.strip().split()
    return parts[1] if len(parts) == 2 and parts[0] == "LEFT_CHAT" else None

def make_chat_msg(nickname: str, message: str) -> str:
    return f"CHAT_MSG {nickname} {message}"

def is_chat_msg(msg: str):
    return msg.startswith("CHAT_MSG ")

def parse_chat_msg(msg: str):
    parts = msg.strip().split(maxsplit=2)
    return (parts[1], parts[2]) if len(parts) == 3 and parts[0] == "CHAT_MSG" else None

# --- Error/Conflict Protocol ---
def make_error(reason: str) -> str:
    return f"ERROR {reason}"

def is_error(msg: str):
    return msg.startswith("ERROR ")

def parse_error(msg: str):
    parts = msg.strip().split(maxsplit=1)
    return parts[1] if len(parts) == 2 and parts[0] == "ERROR" else None

def make_nickname_taken() -> str:
    return "NICKNAME_TAKEN"

def is_nickname_taken(msg: str):
    return msg.strip() == "NICKNAME_TAKEN"