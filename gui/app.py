import tkinter as tk
from ctypes import windll
from gui.main_window import MainWindow
from gui.theme import Theme

def run():
    """Run the GUI application."""
    root = tk.Tk()
    windll.shcore.SetProcessDpiAwareness(1)
    Theme.apply(root)
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    run()