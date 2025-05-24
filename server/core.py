import socket
import threading
from network.tcp import recv_message, send_message
from network.protocol import (
    parse_register, make_joined, make_left, make_broadcast, parse_port,
    make_error, make_nickname_taken
)

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
                except Exception:
                    pass

    def handle_client(self, conn, addr):
        """Handle communication with a connected client."""
        nickname = None
        try:
            data = recv_message(conn)
            reg = parse_register(data)
            tcp_port = None
            if reg:
                nickname, udp_port = reg
                with self.lock:
                    if nickname in self.clients:
                        send_message(conn, make_nickname_taken())
                        conn.close()
                        return
                try:
                    port_msg = recv_message(conn)
                    port_info = parse_port(port_msg)
                    if port_info and port_info[0] == nickname:
                        tcp_port = port_info[1]
                    else:
                        send_message(conn, make_error("Invalid PORT message or nickname mismatch"))
                        conn.close()
                        return
                except Exception as e:
                    send_message(conn, make_error(f"No TCP port received: {e}"))
                    conn.close()
                    return
                with self.lock:
                    self.clients[nickname] = (addr[0], udp_port, tcp_port, conn)
                # Send all current users to the new client
                with self.lock:
                    for other_nick, (other_ip, other_udp, other_tcp, _) in self.clients.items():
                        if other_nick != nickname:
                            send_message(conn, f"JOINED {other_nick} {other_ip} {other_udp} {other_tcp}")
                self.broadcast(f"JOINED {nickname} {addr[0]} {udp_port} {tcp_port}", exclude_nick=nickname)
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
                            else:
                                send_message(conn, make_error("Malformed PORT message or nickname mismatch"))
                        elif msg.startswith("REGISTER "):
                            send_message(conn, make_error("Already registered"))
                        elif msg.startswith("JOINED ") or msg.startswith("LEFT "):
                            send_message(conn, make_error("JOINED/LEFT messages are server-generated only"))
                        elif msg.startswith("ERROR ") or msg.startswith("NICKNAME_TAKEN"):
                            send_message(conn, make_error("Client cannot send error or conflict messages"))
                        else:
                            send_message(conn, make_error("Unknown or unexpected command"))
                    except Exception as e:
                        send_message(conn, make_error(f"Server exception: {e}"))
                        break
            else:
                send_message(conn, make_error("Invalid REGISTER format"))
                conn.close()
                return
        except Exception as e:
            if conn:
                try:
                    send_message(conn, make_error(str(e)))
                except:
                    pass
        finally:
            if nickname:
                with self.lock:
                    if nickname in self.clients:
                        del self.clients[nickname]
                self.broadcast(make_left(nickname), exclude_nick=nickname)
            try:
                conn.close()
            except:
                pass

    def start(self):
        """Start the TCP server and listen for incoming connections."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.host, self.port))
            server_socket.listen()
            def input_thread():
                while True:
                    cmd = input().strip()
                    if cmd.lower() == 'q':
                        self.running = False
                        break
                    elif cmd.lower().startswith('broadcast '):
                        msg = cmd[len('broadcast '):]
                        self.broadcast(make_broadcast(msg))
            threading.Thread(target=input_thread, daemon=True).start()
            while self.running:
                try:
                    server_socket.settimeout(1.0)
                    conn, addr = server_socket.accept()
                    threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()
                except socket.timeout:
                    continue
                except Exception:
                    break