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
            color = COLORS['text']
            if sender == self.nickname:
                color = COLORS['user_text']
            elif sender == "System":
                color = COLORS['system_info']
            else:
                color = COLORS['peer_text']

        self.text.configure(state="normal")
        timestamp = time.strftime("%H:%M:%S")
        self.text.insert(tk.END, f"[{timestamp}] {sender}: ", color)
        self.text.insert(tk.END, f"{message}\n", color)
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
                timestamp = time.strftime("%H:%M:%S")
                self.text.insert(tk.END, f"[{timestamp}] {sender}: ", color)
                self.text.insert(tk.END, f"{message}\n", color)

        self.text.configure(state="disabled")
        self.text.see(tk.END)

    def clear(self):
        """Clear the chat area"""
        self.text.configure(state="normal")
        self.text.delete(1.0, tk.END)
        self.text.configure(state="disabled")