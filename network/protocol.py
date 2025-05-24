"""
Protocol message formats and parsing utilities.
"""

# TCP protocol (Client–Server):
#   Register: REGISTER <nickname> <udp_port>
#   Update:   JOINED <nickname> <ip> <udp_port>
#   Update:   LEFT <nickname>
#   Broadcast: BROADCAST <message>
# UDP protocol (Client–Client):
#   PORT <nickname> <tcp_port>
#   CHAT_REQUEST <nickname>
#   CHAT_ACCEPT <nickname>
#   CHAT_REJECT <nickname>


def parse_register(msg: str):
    # REGISTER <nickname> <udp_port>
    parts = msg.strip().split()
    if len(parts) == 3 and parts[0] == "REGISTER":
        return parts[1], int(parts[2])
    return None

def make_joined(nickname: str, ip: str, udp_port: int) -> str:
    return f"JOINED {nickname} {ip} {udp_port}"

def make_left(nickname: str) -> str:
    return f"LEFT {nickname}"

def make_broadcast(message: str) -> str:
    return f"BROADCAST {message}"

def parse_port(msg: str):
    # PORT <nickname> <tcp_port>
    parts = msg.strip().split()
    if len(parts) == 3 and parts[0] == "PORT":
        return parts[1], int(parts[2])
    return None

def make_port(nickname: str, tcp_port: int) -> str:
    return f"PORT {nickname} {tcp_port}"

# --- Peer-to-peer handshake ---

def make_chat_request(nickname: str) -> str:
    return f"CHAT_REQUEST {nickname}"

def is_chat_request(msg: str):
    return msg.startswith("CHAT_REQUEST ")

def parse_chat_request(msg: str):
    parts = msg.strip().split()
    if len(parts) == 2 and parts[0] == "CHAT_REQUEST":
        return parts[1]
    return None

def make_chat_accept(nickname: str) -> str:
    return f"CHAT_ACCEPT {nickname}"

def is_chat_accept(msg: str):
    return msg.startswith("CHAT_ACCEPT ")

def parse_chat_accept(msg: str):
    parts = msg.strip().split()
    if len(parts) == 2 and parts[0] == "CHAT_ACCEPT":
        return parts[1]
    return None

def make_chat_reject(nickname: str) -> str:
    return f"CHAT_REJECT {nickname}"

def is_chat_reject(msg: str):
    return msg.startswith("CHAT_REJECT ")

def parse_chat_reject(msg: str):
    parts = msg.strip().split()
    if len(parts) == 2 and parts[0] == "CHAT_REJECT":
        return parts[1]
    return None

def make_left_chat(nickname: str) -> str:
    return f"LEFT_CHAT {nickname}"

def is_left_chat(msg: str):
    return msg.startswith("LEFT_CHAT ")

def parse_left_chat(msg: str):
    parts = msg.strip().split()
    if len(parts) == 2 and parts[0] == "LEFT_CHAT":
        return parts[1]
    return None