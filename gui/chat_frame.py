import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import time
from theme.colors import COLORS
from gui.components.peer_list import PeerList
from gui.components.chat_area import ChatArea
from gui.components.message_entry import MessageEntry
from gui.components.broadcast_box import BroadcastBox

class ChatFrame(ttk.Frame):
    def __init__(self, master, client, nickname, on_logout):
        super().__init__(master, padding=10)
        self.client = client
        self.nickname = nickname
        self.on_logout = on_logout
        self.peers = set()
        self.active_peer = None
        self.closed_chats = set()
        self.closing = False

        self._setup_callbacks()
        self._build_ui()

        # Start client threads
        threading.Thread(target=self.client.register, daemon=True).start()
        threading.Thread(target=self.client.start_peer_server, args=(self.client.tcp_port,), daemon=True).start()
        threading.Thread(target=self.client.start_udp_listener, args=(self._handle_udp_msg,), daemon=True).start()

        # Set window close handler
        self.master.protocol("WM_DELETE_WINDOW", self._on_close)

    def _setup_callbacks(self):
        """Set up all client callbacks"""
        self.client.set_callbacks(
            on_peer_message=self._on_peer_message,
            on_peer_connected=self._on_peer_connected,
            on_peer_disconnected=self._on_peer_disconnected,
            on_error=self._on_error,
            on_info=self._on_info,
            on_chat_request=self._on_chat_request,
            on_chat_accept=self._on_chat_accept,
            on_chat_reject=self._on_chat_reject,
            on_peer_accepted=self._on_peer_accepted,
            on_peer_rejected=self._on_peer_rejected,
            on_peer_left=self._on_peer_left,
            on_peer_joined=self._on_peer_joined,
            on_peer_left_server=self._on_peer_left_server,
            on_broadcast=self._on_broadcast,
            on_peer_list=self._on_peer_list,
            on_nickname_taken=self._on_nickname_taken,
            on_file_received=self._on_file_received
        )

    def _build_ui(self):
        """Build the main UI layout"""
        # Configure grid
        self.columnconfigure(0, minsize=220)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)  # Only chat area expands vertically
        self.rowconfigure(1, weight=0)  # Message entry does not expand

        # Left column: Peer list and broadcast
        self.left_frame = ttk.Frame(self)
        self.left_frame.grid(row=0, column=0, rowspan=2, sticky="nsw", padx=(0,16), pady=5)

        # Peer list component
        self.peer_list = PeerList(self.left_frame, self.client)
        self.peer_list.pack(fill='x', padx=2, pady=(0,10))
        self.peer_list.listbox.bind("<<ListboxSelect>>", self._on_select_peer)

        # Broadcast component
        self.broadcast_box = BroadcastBox(self.left_frame, self.client)
        self.broadcast_box.pack(fill='x', padx=2, pady=(0,8))

        # Chat area component
        self.chat_area = ChatArea(self, self.client, self.nickname)
        self.chat_area.grid(row=0, column=1, sticky="nsew", pady=5, padx=(2,2))

        # Message entry component
        self.message_entry = MessageEntry(self, self.client, self.chat_area)
        self.message_entry.grid(row=1, column=1, sticky="ew", pady=(0,0), padx=(0,0))  # No vertical expansion, no extra padding

    def _on_peer_message(self, addr, msg):
        """Handle incoming peer message"""
        if addr not in self.closed_chats:
            nickname = self.client.get_peer_nickname(addr)
            self.chat_area.append_chat(nickname, msg, peer=addr)

    def _on_peer_connected(self, addr):
        """Handle peer connection"""
        nickname = self.client.get_peer_nickname(addr)
        peer_display = f"{nickname} {addr}" if nickname else str(addr)
        self.chat_area.append_chat("System", f"[Peer connected: {peer_display}]",
                                 color=COLORS['chat_connected'],
                                 peer=addr)

    def _on_peer_disconnected(self, addr):
        """Handle peer disconnection"""
        nickname = self.client.get_peer_nickname(addr)
        peer_display = f"{nickname} {addr}" if nickname else str(addr)
        self.chat_area.append_chat("System", f"[Peer disconnected: {peer_display}]",
                                 color=COLORS['chat_disconnected'],
                                 peer=addr)
        if addr in self.client.peer_socks:
            del self.client.peer_socks[addr]
        if addr == self.active_peer:
            self.message_entry.set_state('disabled')

    def _on_chat_request(self, addr, peer_nick, respond):
        """Handle incoming chat request"""
        if messagebox.askyesno("Chat Request", f"{peer_nick} wants to chat. Accept?"):
            respond(True)
            self.chat_area.append_chat("System", f"[Chat accepted with {peer_nick} {addr}]", color=COLORS['chat_accept'], peer=addr)
            self.active_peer = addr
            self.chat_area.active_peer = addr
            self.chat_area.show_chat_history(addr)
            self.message_entry.set_state('normal')
            self.peer_list.refresh_peers(self.peers, self.nickname)
            # Add to peers if not already present
            if addr not in self.peers:
                self.peers.add(addr)
        else:
            respond(False)
            self.chat_area.append_chat("System", f"[Chat rejected with {peer_nick} {addr}]", color=COLORS['chat_reject'], peer=addr)
            self.message_entry.set_state('disabled')

    def _on_chat_accept(self, addr, peer_nick):
        """Handle chat request acceptance"""
        self.client.peer_nicknames[addr] = peer_nick
        self.chat_area.append_chat("System", f"[Chat accepted by {peer_nick} {addr}]", color=COLORS['chat_accept'], peer=addr)
        self.active_peer = addr
        self.chat_area.active_peer = addr
        self.chat_area.show_chat_history(addr)
        self.message_entry.set_state('normal')
        self.peer_list.refresh_peers(self.peers, self.nickname)
        # Add to peers if not already present
        if addr not in self.peers:
            self.peers.add(addr)

    def _on_chat_reject(self, addr, peer_nick):
        """Handle chat request rejection"""
        self.chat_area.append_chat("System", f"[Chat rejected by {peer_nick} {addr}]", color=COLORS['chat_reject'], peer=addr)

    def _on_peer_accepted(self, addr, peer_nick):
        """Handle when we accept a chat"""
        self.chat_area.append_chat("System", f"[You accepted chat with {peer_nick} {addr}]", color=COLORS['chat_accept'], peer=addr)

    def _on_peer_rejected(self, addr, peer_nick):
        """Handle when we reject a chat"""
        self.chat_area.append_chat("System", f"[You rejected chat with {peer_nick} {addr}]", color=COLORS['chat_reject'], peer=addr)

    def _on_peer_left(self, addr, peer_nick):
        """Handle when peer leaves chat"""
        self.closed_chats.add(addr)
        self.chat_area.append_chat("System", f"[{peer_nick} left the chat]", color=COLORS['chat_left'], peer=addr)
        if addr == self.active_peer:
            self.message_entry.set_state('disabled')

    def _on_peer_joined(self, nickname, ip, udp_port):
        """Handle when peer joins server"""
        peer_info = self.client.peers.get(nickname)
        if peer_info and len(peer_info) == 3:
            self.peers.add(peer_info)
            self.peer_list.refresh_peers(self.peers, self.nickname)
            # Show join message in broadcast box instead of chat area
            self._on_broadcast(f"[Peer joined: {nickname} {ip}:{peer_info[2]}]")

    def _on_peer_left_server(self, nickname):
        """Handle when peer leaves server"""
        to_remove = None
        for peer in self.peers:
            if self.client.peers.get(nickname) == peer:
                to_remove = peer
                break
        if to_remove:
            self.peers.remove(to_remove)
        if nickname in self.client.peers:
            del self.client.peers[nickname]
        self.peer_list.refresh_peers(self.peers, self.nickname)
        # Show leave message in broadcast box instead of chat area
        self._on_broadcast(f"[Peer left: {nickname}]")

    def _on_broadcast(self, nickname=None, msg=None):
        """Handle broadcast message

        Args:
            nickname: The nickname of the broadcaster
            msg: The broadcast message
        """
        if nickname and msg:
            self.broadcast_box.append_message(f"{nickname}: {msg}")
        elif nickname:
            # This is a system broadcast (join/leave)
            self.broadcast_box.append_message(f"System: {nickname}")

    def _handle_udp_msg(self, addr, msg):
        """Handle incoming UDP message"""
        self.chat_area.append_chat("System", f"[UDP from {addr}]: {msg}", color=COLORS['chat_udp'], peer=addr)

    def _on_error(self, msg):
        """Handle error messages"""
        if self.closing:
            return
        disconnect_keywords = ["forcibly closed", "disconnected", "left the chat", "aborted by the software", "10053", "10054"]
        if any(kw in msg for kw in disconnect_keywords):
            self.chat_area.append_chat("System", f"[Info] Peer left the chat.", color=COLORS['system_info'])
        else:
            self.chat_area.append_chat("System", f"[Error] {msg}", color=COLORS['system_error'])

    def _on_info(self, msg):
        """Handle info messages"""
        if self.closing:
            return
        self.chat_area.append_chat("System", f"[Info] {msg}", color=COLORS['system_info'])

    def _on_select_peer(self, event):
        """Handle peer selection from list"""
        selection = self.peer_list.listbox.curselection()
        if not selection:
            return
        idx = selection[0]
        nickname = self.peer_list.listbox.get(idx)

        # Find peer_addr by nickname
        peer_info = self.client.peers.get(nickname)
        if not peer_info or len(peer_info) < 3:
            messagebox.showinfo("Peer not available", f"Peer {nickname} is not available.")
            return

        peer_ip, udp_port, tcp_port = peer_info
        peer_addr = (peer_ip, tcp_port)

        # Prevent selecting own chat
        if self.nickname and self.client.peers.get(self.nickname) == peer_info:
            return

        try:
            if peer_addr in self.client.peer_socks and peer_addr not in self.closed_chats:
                self.active_peer = peer_addr
                self.chat_area.active_peer = peer_addr
                self.chat_area.show_chat_history(peer_addr)
                self.message_entry.set_state('normal')
            else:
                sock = self.client.send_tcp_to_peer(peer_ip, tcp_port)
                if sock:
                    self.active_peer = peer_addr
                    self.chat_area.active_peer = peer_addr
                    self.chat_area.show_chat_history(peer_addr)
                    self.message_entry.set_state('normal')
                    # Add to peers if not already present
                    if peer_addr not in self.peers:
                        self.peers.add(peer_addr)
                else:
                    messagebox.showinfo("Connection failed", f"Could not connect to {nickname}. They may be offline or not accepting connections.")
        except Exception as e:
            messagebox.showinfo("Connection failed", f"Could not connect to {nickname}: {e}")

    def _on_close(self):
        """Handle window closing"""
        self.closing = True
        # Close all chats and notify peers
        if self.client:
            for addr in list(self.client.peer_socks.keys()):
                self.client.close_chat(addr)
        self.master.destroy()

    def _on_peer_list(self, peers):
        """Handle peer list update"""
        self.peer_list.refresh_peers(peers, self.nickname)

    def _on_nickname_taken(self):
        """Handle nickname conflict"""
        messagebox.showerror("Error", "Nickname already taken")
        self.on_logout()

    def _on_file_received(self, addr, filename, data):
        """Handle received file"""
        self.chat_area.append_chat("System", f"[File received from {addr}: {filename}]",
                                 color=COLORS['system_info'],
                                 peer=addr)