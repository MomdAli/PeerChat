from network.tcp import send_message, recv_message
from network.udp import listen_for_udp
import network.protocol as prot
import socket
import threading

class PeerClient:
    def __init__(self, server_ip, server_port, nickname, udp_port, tcp_port=None):
        self.server_ip = server_ip
        self.server_port = server_port
        self.nickname = nickname
        self.udp_port = udp_port
        self.tcp_port = tcp_port
        self.running = True
        self.lock = threading.Lock()
        self.peer_socks = {}  # addr -> socket
        self.peer_nicknames = {}  # addr -> nickname
        self.callbacks = {}
        self.server_sock = None
        self.server_listener_thread = None
        self.peers = {}  # nickname -> (ip, udp_port, tcp_port)

    def set_callbacks(self, **kwargs):
        self.callbacks = kwargs

    def _cb(self, name, *args, **kwargs):
        cb = self.callbacks.get(name)
        if cb:
            cb(*args, **kwargs)

    def register(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.server_ip, self.server_port))
            send_message(sock, f"REGISTER {self.nickname} {self.udp_port}")
            if self.tcp_port:
                send_message(sock, prot.make_port(self.nickname, self.tcp_port))
            self.server_sock = sock
            self._cb('on_info', f"Registered with server {self.server_ip}:{self.server_port} as {self.nickname} on UDP port {self.udp_port} and TCP port {self.tcp_port}")
            self.server_listener_thread = threading.Thread(target=self._listen_to_server, daemon=True)
            self.server_listener_thread.start()
        except Exception as e:
            self._cb('on_error', f"Failed to register with server: {e}")

    def _listen_to_server(self):
        sock = self.server_sock
        try:
            while self.running:
                msg = recv_message(sock)
                if not msg:
                    break
                if prot.is_nickname_taken(msg):
                    self._cb('on_nickname_taken')
                    break
                elif prot.is_error(msg):
                    self._cb('on_error', prot.parse_error(msg))
                    break
                elif msg.startswith("JOINED "):
                    parts = msg.strip().split()
                    if len(parts) == 5:
                        nickname, ip, udp_port, tcp_port = parts[1], parts[2], int(parts[3]), int(parts[4])
                        self.peers[nickname] = (ip, udp_port, tcp_port)
                        self._cb('on_peer_joined', nickname, ip, udp_port)
                elif msg.startswith("LEFT "):
                    parts = msg.strip().split()
                    if len(parts) == 2:
                        nickname = parts[1]
                        if nickname in self.peers:
                            del self.peers[nickname]
                        self._cb('on_peer_left_server', nickname)
                elif msg.startswith("BROADCAST "):
                    self._cb('on_broadcast', msg[len("BROADCAST "):])
                elif msg.startswith("PORT "):
                    port_info = prot.parse_port(msg)
                    if port_info:
                        nickname, tcp_port = port_info
                        if nickname in self.peers:
                            ip, udp_port, _ = self.peers[nickname]
                            self.peers[nickname] = (ip, udp_port, tcp_port)
        except Exception as e:
            self._cb('on_error', f"Lost connection to server: {e}")
        finally:
            try:
                sock.close()
            except:
                pass

    def start_peer_server(self, tcp_port):
        def handle_peer(conn, addr):
            def receive_messages():
                try:
                    while True:
                        msg = recv_message(conn)
                        if not msg:
                            break
                        self._handle_peer_message(addr, msg, conn)
                except Exception as e:
                    if not (isinstance(e, OSError) and (getattr(e, 'winerror', None) == 10054 or '10054' in str(e))):
                        self._cb('on_error', f"Peer connection error: {e}")
                finally:
                    try:
                        send_message(conn, prot.make_left_chat(self.nickname))
                    except:
                        pass
                    conn.close()
                    with self.lock:
                        self.peer_socks.pop(addr, None)
                    self._cb('on_peer_disconnected', addr)
            threading.Thread(target=receive_messages, daemon=True).start()
            with self.lock:
                self.peer_socks[addr] = conn
            self._cb('on_peer_connected', addr)
        def tcp_server():
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                server_socket.bind(('', tcp_port))
                server_socket.listen()
                self._cb('on_info', f"Peer server listening on TCP port {tcp_port}...")
                while True:
                    conn, addr = server_socket.accept()
                    threading.Thread(target=handle_peer, args=(conn, addr)).start()
        threading.Thread(target=tcp_server, daemon=True).start()

    def send_tcp_to_peer(self, peer_ip, peer_port):
        addr = (peer_ip, peer_port)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(addr)
            with self.lock:
                self.peer_socks[addr] = sock
            def receive_messages():
                try:
                    while True:
                        msg = recv_message(sock)
                        if not msg:
                            break
                        self._handle_peer_message(addr, msg, sock)
                except Exception as e:
                    if not (isinstance(e, OSError) and (getattr(e, 'winerror', None) == 10054 or '10054' in str(e))):
                        self._cb('on_error', f"[Connection closed] {e}")
                finally:
                    try:
                        send_message(sock, prot.make_left_chat(self.nickname))
                    except:
                        pass
                    sock.close()
                    with self.lock:
                        self.peer_socks.pop(addr, None)
                    self._cb('on_peer_disconnected', addr)
            threading.Thread(target=receive_messages, daemon=True).start()
            self._cb('on_peer_connected', addr)
            send_message(sock, prot.make_chat_request(self.nickname))
            return sock
        except Exception as e:
            self._cb('on_error', f"Failed to connect to peer: {e}")
            return None

    def send_message_to_peer(self, sock, msg):
        try:
            send_message(sock, prot.make_chat_msg(self.nickname, msg))
        except Exception as e:
            self._cb('on_error', f"Failed to send message: {e}")

    def close_chat(self, addr):
        with self.lock:
            sock = self.peer_socks.get(addr)
            if sock:
                try:
                    send_message(sock, prot.make_left_chat(self.nickname))
                except:
                    pass
                try:
                    sock.close()
                except:
                    pass
                self.peer_socks.pop(addr, None)

    def get_peer_nickname(self, addr):
        return self.peer_nicknames.get(addr) or f"Peer{addr[1]}"

    def _handle_peer_message(self, addr, msg, sock):
        if prot.is_chat_request(msg):
            peer_nick = prot.parse_chat_request(msg)
            if not peer_nick:
                send_message(sock, prot.make_error("Malformed CHAT_REQUEST"))
                return
            self.peer_nicknames[addr] = peer_nick
            responded = threading.Event()
            def respond(accept):
                responded.set()
                if accept:
                    send_message(sock, prot.make_chat_accept(self.nickname))
                    self._cb('on_peer_accepted', addr, peer_nick)
                else:
                    send_message(sock, prot.make_chat_reject(self.nickname))
                    self._cb('on_peer_rejected', addr, peer_nick)
            def timeout_watcher():
                if not responded.wait(10):
                    self._cb('on_error', f"No response to chat request from {peer_nick} at {addr} (timeout)")
                    try:
                        send_message(sock, prot.make_error("No response to chat request (timeout)"))
                    except:
                        pass
                    try:
                        sock.close()
                    except:
                        pass
            threading.Thread(target=timeout_watcher, daemon=True).start()
            self._cb('on_chat_request', addr, peer_nick, respond)
            return
        elif prot.is_chat_accept(msg):
            peer_nick = prot.parse_chat_accept(msg)
            if not peer_nick:
                send_message(sock, prot.make_error("Malformed CHAT_ACCEPT"))
                return
            self.peer_nicknames[addr] = peer_nick
            self._cb('on_chat_accept', addr, peer_nick)
            return
        elif prot.is_chat_reject(msg):
            peer_nick = prot.parse_chat_reject(msg)
            if not peer_nick:
                send_message(sock, prot.make_error("Malformed CHAT_REJECT"))
                return
            self.peer_nicknames[addr] = peer_nick
            self._cb('on_chat_reject', addr, peer_nick)
            return
        elif prot.is_left_chat(msg):
            peer_nick = prot.parse_left_chat(msg)
            if not peer_nick:
                send_message(sock, prot.make_error("Malformed LEFT_CHAT"))
                return
            self._cb('on_peer_left', addr, peer_nick)
            return
        elif prot.is_chat_msg(msg):
            parsed = prot.parse_chat_msg(msg)
            if parsed:
                _, message = parsed
                self._cb('on_peer_message', addr, message)
            else:
                send_message(sock, prot.make_error("Malformed CHAT_MSG"))
            return
        elif prot.is_error(msg):
            self._cb('on_error', f"Peer error: {prot.parse_error(msg)}")
            return
        else:
            send_message(sock, prot.make_error("Unknown or unexpected peer message"))
            self._cb('on_error', f"Received unknown peer message: {msg}")

    def start_udp_listener(self, on_message):
        listen_for_udp(self.udp_port, on_message)

    def send_broadcast(self, message):
        if self.server_sock:
            try:
                send_message(self.server_sock, f"BROADCAST {message}")
            except Exception as e:
                self._cb('on_error', f"Failed to send broadcast: {e}")