import socket
import threading
from network.tcp import recv_message, send_message
from network.protocol import parse_register, make_joined, make_left, make_broadcast, parse_port
from theme.colors import COLORS

class PeerServer:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.clients = {}  # nickname: (ip, udp_port, tcp_port, conn)
        self.lock = threading.Lock()
        self.running = True

    def broadcast(self, msg, exclude_nick=None):
        """Send a message to all connected clients except exclude_nick."""
        with self.lock:
            for nick, (ip, udp_port, tcp_port, conn) in list(self.clients.items()):
                if exclude_nick and nick == exclude_nick:
                    continue
                try:
                    send_message(conn, msg)
                except Exception as e:
                    print(f"[ERROR] Failed to send to {nick}: {e}")

    def handle_client(self, conn, addr):
        nickname = None
        try:
            print(f"[INFO] Connection from {addr}")
            data = recv_message(conn)
            reg = parse_register(data)
            tcp_port = None
            if reg:
                nickname, udp_port = reg
                # Wait for PORT message
                try:
                    port_msg = recv_message(conn)
                    port_info = parse_port(port_msg)
                    if port_info and port_info[0] == nickname:
                        tcp_port = port_info[1]
                except Exception as e:
                    print(f"[WARN] No TCP port received from {nickname}: {e}")
                with self.lock:
                    self.clients[nickname] = (addr[0], udp_port, tcp_port, conn)
                print(f"[INFO] Registered {nickname} with UDP port {udp_port} and TCP port {tcp_port}")
                # Send all current users to the new client
                with self.lock:
                    for other_nick, (other_ip, other_udp, other_tcp, _) in self.clients.items():
                        if other_nick != nickname:
                            send_message(conn, f"JOINED {other_nick} {other_ip} {other_udp} {other_tcp}")
                # Notify all others about the new user
                self.broadcast(f"JOINED {nickname} {addr[0]} {udp_port} {tcp_port}", exclude_nick=nickname)
                # Listen for further messages
                while self.running:
                    try:
                        msg = recv_message(conn)
                        if not msg:
                            break
                        if msg.startswith("BROADCAST "):
                            self.broadcast(msg)
                        elif msg.startswith("PORT "):
                            port_info = parse_port(msg)
                            if port_info and port_info[0] == nickname:
                                with self.lock:
                                    ip, udp, _, c = self.clients[nickname]
                                    self.clients[nickname] = (ip, udp, port_info[1], c)
                    except Exception as e:
                        print(f"[ERROR] Client {nickname} error: {e}")
                        break
            else:
                print(f"[ERROR] Unknown command: {data}")
        except Exception as e:
            print(f"[ERROR] Error handling client {addr}: {e}")
        finally:
            if nickname:
                with self.lock:
                    if nickname in self.clients:
                        del self.clients[nickname]
                self.broadcast(make_left(nickname), exclude_nick=nickname)
                print(f"[INFO] {nickname} left and notified others.")
            try:
                conn.close()
            except:
                pass
            print(f"[INFO] Connection closed for {addr}")

    def start(self):
        print(f"[INFO] Starting server on {self.host}:{self.port}")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.host, self.port))
            server_socket.listen()
            print(f"[INFO] Server is listening for connections...")

            def input_thread():
                while True:
                    cmd = input().strip()
                    if cmd.lower() == 'q':
                        print(f"[INFO] Shutting down server...")
                        self.running = False
                        break
                    elif cmd.lower().startswith('broadcast '):
                        msg = cmd[len('broadcast '):]
                        self.broadcast(make_broadcast(msg))
                        print(f"[INFO] Broadcast sent: {msg}")
            threading.Thread(target=input_thread, daemon=True).start()

            while self.running:
                try:
                    server_socket.settimeout(1.0)
                    conn, addr = server_socket.accept()
                    threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"[ERROR] Server error: {e}")
                    break