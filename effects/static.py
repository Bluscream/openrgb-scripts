"""
Static effect - sets devices to a specific color and keeps them static.
"""

from classes import Effect, EffectOptions, Colors
from openrgb.utils import RGBColor


class StaticOptions(EffectOptions):
    """
    Options for static effect.
    """
    
    def __init__(self, 
                 sleep_s: float = 1.0,
                 devices: list = None,
                 max_brightness: float = 1.0,
                 color: str = "white"):
        """
        Initialize static options.
        
        Args:
            color: Color to set (can be a color name like 'red', 'blue', etc. or RGB values like '255,0,0')
            brightness: Brightness multiplier (0.0 to 1.0)
        """
        super().__init__(sleep_s, devices, max_brightness)
        self.color = color
        self.max_brightness = max_brightness


class StaticEffect(Effect):
    """
    Static effect - sets devices to a specific color and keeps them static.
    """
    
    def __init__(self, client, options: StaticOptions):
        super().__init__(client, options)
        self.target_color = None
    
    def _parse_color(self, color_str: str) -> RGBColor:
        """
        Parse color string into RGBColor object.
        
        Args:
            color_str: Color string (e.g., 'red', '255,0,0', '#FF0000')
            
        Returns:
            RGBColor object
        """
        color_str = color_str.strip().lower()
        
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
    
    def _kill_own_process(self):
        """
        Kill the own process.
        """
        import os
        os.kill(os.getpid(), signal.SIGKILL)
        import sys
        sys.exit(0)

    def start(self):
        """Initialize the effect."""
        print(f"Starting static effect with color: {self.options.color}, brightness: {self.options.max_brightness}")
        self.target_color = self._parse_color(self.options.color)
        # Apply brightness to the color and clamp to valid range
        r = max(0, min(255, int(self.target_color.red * self.options.max_brightness)))
        g = max(0, min(255, int(self.target_color.green * self.options.max_brightness)))
        b = max(0, min(255, int(self.target_color.blue * self.options.max_brightness)))
        self.target_color = RGBColor(r, g, b)
        # Set the color immediately
        self.set_all_target_devices_color(self.target_color)

        # self._kill_own_process()
    
    def loop(self):
        """Execute one iteration of the static effect."""
        # For static effect, we just maintain the same color
        # The color is already set in start(), so we don't need to do anything here
        pass
    
    def stop(self):
        """Clean up the effect."""
        # Don't turn off devices when stopping static effect
        # This allows the color to persist 