import socket
from typing import Callable

def listen_for_udp(port: int, on_message: Callable):
    def udp_server():
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind(('', port))
            while True:
                data, addr = sock.recvfrom(1024)
                if data:
                    message = data.decode()
                    on_message(addr, message)
    import threading
    threading.Thread(target=udp_server, daemon=True).start()

def send_udp(target_ip: str, target_port: int, message: str):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(message.encode(), (target_ip, target_port))