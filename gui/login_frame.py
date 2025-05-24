import tkinter as tk
from tkinter import ttk, messagebox
import socket
import threading
from client.core import PeerClient
from theme.colors import COLORS
from gui.theme import Theme

class LoginFrame(ttk.Frame):
    def __init__(self, master, on_login_success):
        super().__init__(master, padding=30)
        self.on_login_success = on_login_success
        self._build_ui()

    def _build_ui(self):
        # Configure grid
        self.columnconfigure(1, weight=1)

        # Login header
        header = ttk.Label(self, text="Login",
                          font=Theme.get_header_font(),
                          background=COLORS['background'],
                          foreground=COLORS['accent'])
        header.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Nickname field
        ttk.Label(self, text="Nickname:",
                 font=Theme.get_text_font(),
                 background=COLORS['background'],
                 foreground=COLORS['system_info']).grid(row=1, column=0, sticky="e", pady=6)

        self.nickname_entry = tk.Entry(self,
                                     font=Theme.get_entry_font(),
                                     bg=COLORS['entry_bg'],
                                     fg=COLORS['chat_input'],
                                     insertbackground=COLORS['accent'],
                                     borderwidth=1,
                                     relief='flat')
        self.nickname_entry.grid(row=1, column=1, sticky="ew", pady=6)

        # Server IP field
        ttk.Label(self, text="Server IP:",
                 font=Theme.get_text_font(),
                 background=COLORS['background'],
                 foreground=COLORS['system_info']).grid(row=2, column=0, sticky="e", pady=6)

        self.server_entry = tk.Entry(self,
                                   font=Theme.get_entry_font(),
                                   bg=COLORS['entry_bg'],
                                   fg=COLORS['chat_input'],
                                   insertbackground=COLORS['accent'],
                                   borderwidth=1,
                                   relief='flat')
        self.server_entry.insert(0, "127.0.0.1")
        self.server_entry.grid(row=2, column=1, sticky="ew", pady=6)

        # Server Port field
        ttk.Label(self, text="Server Port:",
                 font=Theme.get_text_font(),
                 background=COLORS['background'],
                 foreground=COLORS['system_info']).grid(row=3, column=0, sticky="e", pady=6)

        self.port_entry = tk.Entry(self,
                                 font=Theme.get_entry_font(),
                                 bg=COLORS['entry_bg'],
                                 fg=COLORS['chat_input'],
                                 insertbackground=COLORS['accent'],
                                 borderwidth=1,
                                 relief='flat')
        self.port_entry.insert(0, "12345")
        self.port_entry.grid(row=3, column=1, sticky="ew", pady=6)

        # Connect button
        self.connect_btn = tk.Button(self, text="Connect",
                                   command=self._on_connect,
                                   font=Theme.get_button_font(),
                                   bg=COLORS['button_bg'],
                                   fg=COLORS['button_text'],
                                   activebackground=COLORS['button_hover'],
                                   activeforeground=COLORS['button_text'],
                                   borderwidth=0,
                                   relief='flat',
                                   highlightthickness=2,
                                   highlightbackground=COLORS['accent'])
        self.connect_btn.grid(row=4, column=0, columnspan=2, pady=18)

        # Bind enter key to connect
        self.nickname_entry.bind('<Return>', lambda e: self._on_connect())
        self.server_entry.bind('<Return>', lambda e: self._on_connect())
        self.port_entry.bind('<Return>', lambda e: self._on_connect())

        # Set initial focus
        self.nickname_entry.focus()

    def _find_free_port(self):
        """Find a free port for UDP/TCP connections"""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', 0))
        port = s.getsockname()[1]
        s.close()
        return port

    def _on_connect(self):
        """Handle connection attempt"""
        nickname = self.nickname_entry.get().strip()
        server_ip = self.server_entry.get().strip()
        try:
            server_port = int(self.port_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Invalid port number")
            return

        if not nickname:
            messagebox.showerror("Error", "Nickname required")
            return

        # Find free ports for UDP and TCP
        udp_port = self._find_free_port()
        tcp_port = self._find_free_port()

        # Create client instance
        client = PeerClient(server_ip, server_port, nickname, udp_port, tcp_port)

        # Pass client to callback
        self.on_login_success(client, nickname)

    def destroy(self):
        """Clean up resources before destroying the frame"""
        super().destroy()