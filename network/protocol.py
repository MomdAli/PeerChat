"""
Protocol message formats and parsing utilities for PeerChat.
"""

# --- Client-Server Protocol ---
def parse_register(msg: str):
    # Accepts: REGISTER "nickname with spaces" <udp_port>
    prefix = "REGISTER "
    if msg.startswith(prefix):
        content = msg[len(prefix):].strip()
        if content.startswith('"'):
            end_quote = content.find('"', 1)
            if end_quote == -1:
                return None
            nickname = content[1:end_quote]
            rest = content[end_quote+1:].strip()
            try:
                udp_port = int(rest)
                return nickname, udp_port
            except Exception:
                return None
        else:
            # fallback for old format (no quotes)
            parts = content.rsplit(' ', 1)
            if len(parts) == 2:
                nickname, port_str = parts
                try:
                    return nickname, int(port_str)
                except ValueError:
                    return None
    return None

def make_register(nickname: str, udp_port: int) -> str:
    # Always quote the nickname to preserve spaces
    return f'REGISTER "{nickname}" {udp_port}'

def make_joined(nickname: str, ip: str, udp_port: int, tcp_port: int) -> str:
    # Always quote the nickname to preserve spaces
    return f'JOINED "{nickname}" {ip} {udp_port} {tcp_port}'

def parse_joined(msg: str):
    # Accepts: JOINED "nickname with spaces" <ip> <udp_port> <tcp_port>
    prefix = "JOINED "
    if msg.startswith(prefix):
        content = msg[len(prefix):].strip()
        if content.startswith('"'):
            end_quote = content.find('"', 1)
            if end_quote == -1:
                return None
            nickname = content[1:end_quote]
            rest = content[end_quote+1:].strip().split()
            if len(rest) == 3:
                ip, udp_str, tcp_str = rest
                try:
                    return nickname, ip, int(udp_str), int(tcp_str)
                except ValueError:
                    return None
        else:
            # Fallback for unquoted nickname: parts = nickname ip udp tcp
            parts = content.split()
            if len(parts) == 4:
                nickname, ip, udp_str, tcp_str = parts
                try:
                    return nickname, ip, int(udp_str), int(tcp_str)
                except ValueError:
                    return None
    return None

def make_left(nickname: str) -> str:
    return f"LEFT {nickname}"

def make_broadcast(message: str) -> str:
    return f"BROADCAST {message}"

def parse_port(msg: str):
    # Message format: PORT <nickname_with_spaces> <tcp_port>
    prefix = "PORT "
    if msg.startswith(prefix):
        content = msg[len(prefix):].strip()
        parts = content.rsplit(' ', 1)
        if len(parts) == 2:
            nickname, port_str = parts
            try:
                return nickname, int(port_str)
            except ValueError:
                return None
    return None

def make_port(nickname: str, tcp_port: int) -> str:
    return f"PORT {nickname} {tcp_port}"

# --- Peer-to-Peer Protocol ---
def make_chat_request(nickname: str) -> str:
    return f"CHAT_REQUEST {nickname}"

def is_chat_request(msg: str):
    return msg.startswith("CHAT_REQUEST ")

def parse_chat_request(msg: str):
    prefix = "CHAT_REQUEST "
    if msg.startswith(prefix):
        nickname = msg[len(prefix):].strip()
        return nickname if nickname else None
    return None

def make_chat_accept(nickname: str) -> str:
    return f"CHAT_ACCEPT {nickname}"

def is_chat_accept(msg: str):
    return msg.startswith("CHAT_ACCEPT ")

def parse_chat_accept(msg: str):
    prefix = "CHAT_ACCEPT "
    if msg.startswith(prefix):
        nickname = msg[len(prefix):].strip()
        return nickname if nickname else None
    return None

def make_chat_reject(nickname: str) -> str:
    return f"CHAT_REJECT {nickname}"

def is_chat_reject(msg: str):
    return msg.startswith("CHAT_REJECT ")

def parse_chat_reject(msg: str):
    prefix = "CHAT_REJECT "
    if msg.startswith(prefix):
        nickname = msg[len(prefix):].strip()
        return nickname if nickname else None
    return None

def make_left_chat(nickname: str) -> str:
    return f"LEFT_CHAT {nickname}"

def is_left_chat(msg: str):
    return msg.startswith("LEFT_CHAT ")

def parse_left_chat(msg: str):
    prefix = "LEFT_CHAT "
    if msg.startswith(prefix):
        nickname = msg[len(prefix):].strip()
        return nickname if nickname else None
    return None

def make_chat_msg(nickname: str, message: str) -> str:
    return f'CHAT_MSG "{nickname}" {message}' # Nickname is quoted

def is_chat_msg(msg: str):
    return msg.startswith("CHAT_MSG ")

def parse_chat_msg(msg: str):
    # Message format: CHAT_MSG "<nickname_with_spaces>" <message_content>
    prefix = "CHAT_MSG "
    if not msg.startswith(prefix):
        return None
    content = msg[len(prefix):].strip()

    if not content.startswith('"'):
        # Fallback for old format or unquoted nickname (treat first word as nick)
        # This part can be removed if strict quoting is enforced everywhere
        parts = content.split(' ', 1)
        if len(parts) == 2:
            return parts[0], parts[1]
        elif len(parts) == 1: # Nickname only, empty message
             return parts[0], ""
        return None

    end_quote_idx = content.find('"', 1)
    if end_quote_idx == -1:
        return None # Malformed, no closing quote

    nickname = content[1:end_quote_idx]
    message = content[end_quote_idx+1:].lstrip() # +1 to skip quote, lstrip for space after quote
    return nickname, message

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