import tkinter as tk
from gui.login_frame import LoginFrame
from gui.chat_frame import ChatFrame

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Peer-to-Peer Chat Client")
        self.root.geometry("900x650")
        self.root.resizable(True, True)
        self.current_frame = None
        self.show_login()

    def show_login(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = LoginFrame(self.root, self.on_login_success)
        self.current_frame.pack(expand=True, fill='both')

    def show_chat(self, client, nickname):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = ChatFrame(self.root, client, nickname, self.show_login)
        self.current_frame.pack(expand=True, fill='both')

    def on_login_success(self, client, nickname):
        self.show_chat(client, nickname)