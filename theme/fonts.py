"""Font configurations for the application."""

# Primary font stack with fallbacks
FONTS = {
    'primary': ('Open Sans', 'Segoe UI', 'Arial', 'sans-serif'),
    'monospace': ('Consolas', 'Monaco', 'Courier New', 'monospace')
}

# Font sizes for different purposes
SIZES = {
    'small': 12,
    'normal': 15,
    'large': 18,
    'header': 20
}

# Font styles
STYLES = {
    'normal': 'normal',
    'bold': 'bold',
    'italic': 'italic'
}

def get_font(family='primary', size='normal', style='normal'):
    """Get a font tuple with the specified configuration."""
    font_family = FONTS[family][0]  # Use first font in stack as primary
    font_size = SIZES[size]
    font_style = STYLES[style]
    return (font_family, font_size, font_style)

# Default font configuration
DEFAULT_FONT = get_font()