import tkinter as tk
from tkinter import ttk, simpledialog
from theme.colors import COLORS
from gui.theme import Theme

class PeerList(ttk.Frame):
    def __init__(self, master, client):
        super().__init__(master)
        self.client = client

        # Peer list label
        self.peer_list_label = tk.Label(self, text="Peer list",
                                      font=Theme.get_header_font(),
                                      bg=COLORS['background'],
                                      fg=COLORS['text'],
                                      anchor='w')
        self.peer_list_label.pack(fill='x', padx=2, pady=(0,2))

        # Peer list
        self.listbox = tk.Listbox(self, height=13, width=20,
                                 font=Theme.get_text_font(),
                                 bg=COLORS['chat_bg'],
                                 fg=COLORS['button_text'],
                                 highlightbackground=COLORS['border'],
                                 highlightthickness=1,
                                 selectbackground=COLORS['button_hover'],
                                 selectforeground=COLORS['button_text'],
                                 borderwidth=1, relief='solid')
        self.listbox.pack(fill='x', padx=2, pady=(0,10))

        # Connect to Peer button
        self.connect_peer_btn = tk.Button(self, text="Connect to Peer",
                                        command=self._on_connect_peer,
                                        font=Theme.get_button_font(),
                                        bg=COLORS['button_bg'],
                                        fg=COLORS['button_text'],
                                        activebackground=COLORS['button_hover'],
                                        activeforeground=COLORS['button_text'],
                                        borderwidth=0, relief='flat',
                                        highlightthickness=2,
                                        highlightbackground=COLORS['accent'])
        self.connect_peer_btn.pack(fill='x', pady=(0,8))

        # Logged in as label
        self.logged_in_label = tk.Label(self, text=f"Logged in as: {self.client.nickname}",
                                      font=Theme.get_text_font(),
                                      bg=COLORS['background'],
                                      fg=COLORS['text'])
        self.logged_in_label.pack(anchor='w', pady=(0,8))

    def refresh_peers(self, peers, local_nickname):
        """Update the peer list display"""
        self.listbox.delete(0, tk.END)

        # Create a list of nicknames from peers
        nicknames = []
        for nickname, peer_info in self.client.peers.items():
            # Skip own nickname
            if nickname == local_nickname:
                continue
            # Add nickname to list if peer info is valid
            if peer_info and len(peer_info) >= 2:
                nicknames.append(nickname)

        # Sort and display nicknames
        for nickname in sorted(nicknames):
            self.listbox.insert(tk.END, nickname)

    def _on_connect_peer(self):
        """Handle manual peer connection"""
        from tkinter import simpledialog
        peer_ip = simpledialog.askstring("Peer IP", "Enter peer IP:")
        peer_port = simpledialog.askinteger("Peer TCP Port", "Enter peer TCP port:")
        if not peer_ip:
            peer_ip = "127.0.0.1"
        if not peer_port:
            try:
                my_port = int(self.client.tcp_port)
                peer_port = my_port + 1
            except:
                peer_port = 4001

        # Try to establish connection
        sock = self.client.send_tcp_to_peer(peer_ip, peer_port)
        if sock:
            peer_addr = (peer_ip, peer_port)
            # Do not enable chat until chat accept is received
            if hasattr(self.master.master, 'active_peer'):
                self.master.master.active_peer = peer_addr
            if hasattr(self.master.master, 'chat_area'):
                self.master.master.chat_area.active_peer = peer_addr
                self.master.master.chat_area.show_chat_history(peer_addr)
            if hasattr(self.master.master, 'message_entry'):
                self.master.master.message_entry.set_state('disabled')  # Wait for chat accept