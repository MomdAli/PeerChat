import tkinter as tk
from tkinter import ttk, simpledialog
from theme.colors import COLORS
from gui.theme import Theme
import time

class BroadcastBox(ttk.Frame):
    def __init__(self, master, client):
        super().__init__(master)
        self.client = client

        # Configure frame to fill horizontally
        self.pack(fill='x', expand=True)

        # Broadcast label
        self.broadcast_label = tk.Label(self, text="Broadcast",
                                      font=Theme.get_header_font(),
                                      bg=COLORS['background'],
                                      fg=COLORS['text'],
                                      anchor='w')
        self.broadcast_label.pack(fill='x', padx=2, pady=(0,2))

        # Broadcast text area - fixed height but expandable width
        self.text = tk.Text(self, wrap=tk.WORD, state="disabled",
                           font=Theme.get_text_font(),
                           width=1, height=6,
                           bg=COLORS['chat_bg'],
                           fg=COLORS['broadcast'],
                           insertbackground=COLORS['accent'],
                           borderwidth=1, relief='solid',
                           highlightbackground=COLORS['border'],
                           highlightthickness=1)
        self.text.pack(fill='x', padx=2, pady=(0,8))

        # Configure color tags
        self.text.tag_config('timestamp', foreground=COLORS['timestamp'])
        self.text.tag_config('broadcast', foreground=COLORS['broadcast'])
        self.text.tag_config('error', foreground=COLORS['system_error'])

        # Broadcast button
        self.broadcast_btn = tk.Button(self, text="Broadcast",
                                     command=self._on_broadcast,
                                     font=Theme.get_button_font(),
                                     bg=COLORS['button_bg'],
                                     fg=COLORS['button_text'],
                                     activebackground=COLORS['button_hover'],
                                     activeforeground=COLORS['button_text'],
                                     borderwidth=0, relief='flat',
                                     highlightthickness=2,
                                     highlightbackground=COLORS['accent'])
        self.broadcast_btn.pack(fill='x', padx=2, pady=(0,8))

    def _on_broadcast(self):
        """Handle broadcast message sending"""
        msg = simpledialog.askstring("Broadcast Message", "Enter message to broadcast:")
        if msg and msg.strip():
            try:
                self.client.send_broadcast(msg.strip())
                self.append_message(f"You (broadcast): {msg.strip()}")
            except Exception as e:
                self.append_message(f"System: Error sending broadcast - {str(e)}", is_error=True)

    def append_message(self, message, is_error=False):
        """Add a broadcast message to the display

        Args:
            message: The message to display
            is_error: Whether this is an error message
        """
        self.text.configure(state="normal")
        timestamp = time.strftime("%H:%M:%S")
        tag = 'error' if is_error else 'broadcast'
        self.text.insert(tk.END, f"[{timestamp}] ", 'timestamp')
        self.text.insert(tk.END, f"{message}\n", tag)
        self.text.configure(state="disabled")
        self.text.see(tk.END)

    def clear(self):
        """Clear the broadcast box"""
        self.text.configure(state="normal")
        self.text.delete(1.0, tk.END)
        self.text.configure(state="disabled")