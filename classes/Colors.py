"""
Color definitions for OpenRGB effects.
"""

import random
from enum import Enum
from openrgb.utils import RGBColor


class Colors(Enum):
    """
    Enumeration of predefined colors for OpenRGB effects.
    """
    RED = RGBColor(255, 0, 0)
    ORANGE = RGBColor(255, 127, 0)
    YELLOW = RGBColor(255, 255, 0)
    GREEN = RGBColor(0, 255, 0)
    BLUE = RGBColor(0, 0, 255)
    INDIGO = RGBColor(75, 0, 130)
    VIOLET = RGBColor(148, 0, 211)
    WHITE = RGBColor(255, 255, 255)
    BLACK = RGBColor(0, 0, 0)
    CYAN = RGBColor(0, 255, 255)
    MAGENTA = RGBColor(255, 0, 255)
    PINK = RGBColor(255, 192, 203)
    BROWN = RGBColor(165, 42, 42)
    GRAY = RGBColor(128, 128, 128)
    LIGHT_GRAY = RGBColor(211, 211, 211)
    DARK_GRAY = RGBColor(169, 169, 169)
    LIGHT_BLUE = RGBColor(173, 216, 230)


# Rainbow color sequence
RAINBOW_COLORS = [
    Colors.RED.value,
    Colors.ORANGE.value,
    Colors.YELLOW.value,
    Colors.GREEN.value,
    Colors.BLUE.value,
    Colors.INDIGO.value,
    Colors.VIOLET.value,
]


def parse_color(color_str: str) -> RGBColor:
    """
    Parse color string into RGBColor object.
    
    Args:
        color_str: Color string (e.g., 'red', '255,0,0', '#FF0000', 'random')
        
    Returns:
        RGBColor object
        
    Example:
        # Parse different color formats
        red = parse_color('red')
        purple = parse_color('255,0,255')
        green = parse_color('#00FF00')
        random_color = parse_color('random')
    """
    color_str = color_str.strip().lower()
    
    # Handle random color
    if color_str == "random":
        # Random color from available colors (excluding black)
        available_colors = [color.value for color in Colors if color != Colors.BLACK]
        return random.choice(available_colors)
    
    # Check if it's a predefined color name
    if hasattr(Colors, color_str.upper()):
        return getattr(Colors, color_str.upper()).value
    
    # Check if it's RGB values (comma-separated)
    if ',' in color_str:
        try:
            parts = color_str.split(',')
            if len(parts) == 3:
                r = int(parts[0].strip())
                g = int(parts[1].strip())
                b = int(parts[2].strip())
                return RGBColor(r, g, b)
        except ValueError:
            pass
    
    # Check if it's a hex color
    if color_str.startswith('#'):
        try:
            hex_color = color_str[1:]  # Remove #
            if len(hex_color) == 6:
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                return RGBColor(r, g, b)
        except ValueError:
            pass
    
    # Default to white if parsing fails
    print(f"Warning: Could not parse color '{color_str}', using white")
    return Colors.WHITE.value


def lerp_color(color1: RGBColor, color2: RGBColor, t: float) -> RGBColor:
    """
    Linearly interpolate between two RGBColor objects.
    
    Args:
        color1: Starting RGBColor
        color2: Ending RGBColor  
        t: Interpolation factor (0.0 to 1.0)
        
    Returns:
        Interpolated RGBColor object
        
    Example:
        # Interpolate 50% between red and blue
        mid_color = lerp_color(Colors.RED.value, Colors.BLUE.value, 0.5)
    """
    r = int(color1.red + (color2.red - color1.red) * t)
    g = int(color1.green + (color2.green - color1.green) * t)
    b = int(color1.blue + (color2.blue - color1.blue) * t)
    return RGBColor(r, g, b) 