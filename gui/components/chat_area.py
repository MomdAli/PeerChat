import tkinter as tk
from tkinter import ttk
from theme.colors import COLORS
from gui.theme import Theme
import time

class ChatArea(ttk.Frame):
    def __init__(self, master, client, nickname):
        super().__init__(master)
        self.client = client
        self.nickname = nickname
        self.active_peer = None
        self.chat_history = {}

        # Chat text area
        self.text = tk.Text(self, wrap=tk.WORD, state="disabled",
                           font=Theme.get_text_font(),
                           width=40, height=20,
                           bg=COLORS['chat_bg'],
                           fg=COLORS['text'],
                           insertbackground=COLORS['accent'],
                           borderwidth=1,
                           relief='solid',
                           highlightbackground=COLORS['border'],
                           highlightthickness=1)
        self.text.pack(fill='both', expand=True, padx=2)

        # Configure color tags for different message types
        self.text.tag_config('timestamp', foreground=COLORS['timestamp'])
        self.text.tag_config('user', foreground=COLORS['user_text'])
        self.text.tag_config('peer', foreground=COLORS['peer_text'])
        self.text.tag_config('system', foreground=COLORS['system_info'])
        self.text.tag_config('error', foreground=COLORS['system_error'])
        self.text.tag_config('broadcast', foreground=COLORS['broadcast'])
        self.text.tag_config('left', foreground=COLORS['chat_left'])
        self.text.tag_config('accept', foreground=COLORS['chat_accept'])
        self.text.tag_config('reject', foreground=COLORS['chat_reject'])
        self.text.tag_config('connected', foreground=COLORS['chat_connected'])
        self.text.tag_config('disconnected', foreground=COLORS['chat_disconnected'])
        self.text.tag_config('udp', foreground=COLORS['chat_udp'])

        # Create scrollbar
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.text.yview)
        scrollbar.pack(side='right', fill='y')
        self.text['yscrollcommand'] = scrollbar.set

    def append_chat(self, sender, message, color=None, peer=None):
        """Add a message to the chat display

        Args:
            sender: The sender of the message
            message: The message content
            color: Optional color override for the message
            peer: Optional peer address for storing in specific chat history
        """
        if not color:
            if sender == self.nickname:
                tag = 'user'
                color = COLORS['user_text']
            elif sender == "System":
                tag = 'system'
                color = COLORS['system_info']
            else:
                tag = 'peer'
                color = COLORS['peer_text']
        else:
            # Map color to tag if possible
            tag_map = {
                COLORS['user_text']: 'user',
                COLORS['peer_text']: 'peer',
                COLORS['system_info']: 'system',
                COLORS['system_error']: 'error',
                COLORS['broadcast']: 'broadcast',
                COLORS['chat_left']: 'left',
                COLORS['chat_accept']: 'accept',
                COLORS['chat_reject']: 'reject',
                COLORS['chat_connected']: 'connected',
                COLORS['chat_disconnected']: 'disconnected',
                COLORS['chat_udp']: 'udp',
            }
            tag = tag_map.get(color, 'peer')

        self.text.configure(state="normal")
        timestamp = time.strftime("%H:%M:%S")
        self.text.insert(tk.END, f"[{timestamp}] ", 'timestamp')
        self.text.insert(tk.END, f"{sender}: ", tag)
        self.text.insert(tk.END, f"{message}\n", tag)
        self.text.configure(state="disabled")
        self.text.see(tk.END)

        # Store in chat history
        target_peer = peer if peer is not None else self.active_peer
        if target_peer:
            if target_peer not in self.chat_history:
                self.chat_history[target_peer] = []
            self.chat_history[target_peer].append((sender, message, color))

    def show_chat_history(self, peer_addr):
        """Display chat history for the given peer"""
        self.active_peer = peer_addr
        self.text.configure(state="normal")
        self.text.delete(1.0, tk.END)

        if peer_addr in self.chat_history:
            for sender, message, color in self.chat_history[peer_addr]:
                if sender == self.nickname:
                    tag = 'user'
                elif sender == "System":
                    tag = 'system'
                else:
                    tag = 'peer'
                timestamp = time.strftime("%H:%M:%S")
                self.text.insert(tk.END, f"[{timestamp}] ", 'timestamp')
                self.text.insert(tk.END, f"{sender}: ", tag)
                self.text.insert(tk.END, f"{message}\n", tag)

        self.text.configure(state="disabled")
        self.text.see(tk.END)

    def clear(self):
        """Clear the chat area"""
        self.text.configure(state="normal")
        self.text.delete(1.0, tk.END)
        self.text.configure(state="disabled")