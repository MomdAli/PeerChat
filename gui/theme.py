"""Theme configuration for the GUI application."""

import tkinter as tk
from tkinter import ttk
from theme.colors import COLORS
from theme.fonts import get_font, DEFAULT_FONT

class Theme:
    @staticmethod
    def apply(root):
        """Apply theme to the root window and all widgets."""
        style = ttk.Style(root)
        if 'vista' in style.theme_names():
            style.theme_use('vista')
        else:
            style.theme_use('clam')

        # Configure default font and colors
        style.configure('.',
            background=COLORS['background'],
            foreground=COLORS['text'],
            font=DEFAULT_FONT
        )

        # Button styling
        style.configure('TButton',
            background=COLORS['button_bg'],
            foreground=COLORS['button_text'],
            font=DEFAULT_FONT,
            borderwidth=0,
            focusthickness=3,
            focuscolor=COLORS['accent']
        )
        style.map('TButton',
            background=[('active', COLORS['button_hover'])],
            foreground=[('active', COLORS['button_text'])]
        )

        # Entry styling
        style.configure('TEntry',
            fieldbackground=COLORS['entry_bg'],
            foreground=COLORS['chat_input'],
            font=DEFAULT_FONT,
            borderwidth=1
        )

        # Label styling
        style.configure('TLabel',
            background=COLORS['background'],
            foreground=COLORS['text'],
            font=DEFAULT_FONT
        )

        # Frame styling
        style.configure('TFrame',
            background=COLORS['background']
        )

        # Configure root window
        root.configure(bg=COLORS['background'])

    @staticmethod
    def get_text_font():
        """Get the font configuration for text widgets."""
        return get_font()

    @staticmethod
    def get_header_font():
        """Get the font configuration for headers."""
        return get_font(size='large', style='bold')

    @staticmethod
    def get_button_font():
        """Get the font configuration for buttons."""
        return get_font()

    @staticmethod
    def get_entry_font():
        """Get the font configuration for entry widgets."""
        return get_font()