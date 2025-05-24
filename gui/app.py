import tkinter as tk
import sys
from gui.main_window import MainWindow
from gui.theme import Theme

def run():
    """Run the GUI application."""
    root = tk.Tk()
    if sys.platform.startswith('win'):
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass
    Theme.apply(root)
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    run()