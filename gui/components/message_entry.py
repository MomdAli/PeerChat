import tkinter as tk
from tkinter import ttk
from theme.colors import COLORS
from gui.theme import Theme

class MessageEntry(ttk.Frame):
    def __init__(self, master, client, chat_area):
        super().__init__(master)
        self.client = client
        self.chat_area = chat_area

        self.columnconfigure(0, weight=1)

        # Message entry
        self.entry = tk.Entry(self,
                            font=Theme.get_entry_font(),
                            bg=COLORS['entry_bg'],
                            fg=COLORS['chat_input'],
                            insertbackground=COLORS['accent'])
        self.entry.grid(row=0, column=0, sticky="ew", padx=(0,8))
        self.entry.bind("<Return>", self._on_send)

        # Send button
        self.send_btn = tk.Button(self, text="Send",
                                command=self._on_send,
                                font=Theme.get_button_font(),
                                bg=COLORS['button_bg'],
                                fg=COLORS['button_text'],
                                activebackground=COLORS['button_hover'],
                                activeforeground=COLORS['button_text'],
                                borderwidth=0, relief='flat',
                                highlightthickness=2,
                                highlightbackground=COLORS['accent'])
        self.send_btn.grid(row=0, column=1, padx=(0,8))

        # Close chat button
        self.close_chat_btn = tk.Button(self, text="Close Chat", command=self._on_close_chat,
                                       font=Theme.get_button_font(),
                                       bg=COLORS['button_bg'],
                                       fg=COLORS['button_text'],
                                       activebackground=COLORS['button_hover'],
                                       activeforeground=COLORS['button_text'],
                                       borderwidth=0, relief='flat',
                                       highlightthickness=2,
                                       highlightbackground=COLORS['accent'])
        self.close_chat_btn.grid(row=0, column=2)

        # Initially disable controls
        self.set_state('disabled')

    def _on_send(self, event=None):
        """Handle message sending"""
        msg = self.entry.get().strip()
        if not msg or not self.chat_area.active_peer:
            return

        if self.chat_area.active_peer not in self.client.peer_socks or \
           self.chat_area.active_peer in getattr(self.master, 'closed_chats', set()):
            return

        # Send message to peer
        try:
            sock = self.client.peer_socks[self.chat_area.active_peer]
            self.client.send_message_to_peer(sock, msg)
            # Add message to chat history
            self.chat_area.append_chat(self.client.nickname, msg)
            # Clear entry
            self.entry.delete(0, tk.END)
        except Exception as e:
            self.chat_area.append_chat("System", f"[Error] Failed to send message: {str(e)}", color=COLORS['system_error'])

    def _on_close_chat(self):
        """Handle chat closing"""
        if self.chat_area.active_peer:
            self.client.close_chat(self.chat_area.active_peer)
            if hasattr(self.master, 'closed_chats'):
                self.master.closed_chats.add(self.chat_area.active_peer)
            self.chat_area.append_chat("System", "[You left the chat]", color=COLORS['chat_left'])
            self.set_state('disabled')

    def set_state(self, state):
        """Enable/disable all controls"""
        self.entry.config(state=state)
        if state == 'disabled':
            self.entry.config(bg=COLORS['entry_bg_disabled'], fg=COLORS['button_text'])
        else:
            self.entry.config(bg=COLORS['entry_bg'], fg=COLORS['chat_input'])
        self.send_btn.config(state=state)
        self.close_chat_btn.config(state=state)