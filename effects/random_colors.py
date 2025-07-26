"""
Random colors effect - randomly changing colors on devices.
"""

import random
import time
from classes import Effect, EffectOptions, Colors


class RandomColorsOptions(EffectOptions):
    """
    Options for random colors effect.
    """
    
    def __init__(self, 
                 sleep_s: float = 0.5,
                 devices: list = None,
                 max_brightness: float = 1.0,
                 per_device: bool = True,
                 color_palette: list = None):
        """
        Initialize random colors options.
        
        Args:
            per_device: Whether to set each device to a different random color
            color_palette: List of RGBColor objects to choose from (None for default colors)
        """
        super().__init__(sleep_s, devices, max_brightness)
        self.per_device = per_device
        self.color_palette = color_palette


class RandomColorsEffect(Effect):
    """
    Random colors effect - randomly changing colors on devices.
    
    This effect can either set each device to a different random color
    or set all devices to the same random color. The color palette can
    be customized or use the default set of colors.
    """
    
    def __init__(self, client, options: RandomColorsOptions):
        super().__init__(client, options)
        self.available_colors = []
    
    def start(self):
        """Initialize the effect."""
        print("Starting random colors effect...")
        
        # Set up available colors
        if self.options.color_palette is not None and self.options.color_palette:
            # Validate that color_palette contains RGBColor objects
            if isinstance(self.options.color_palette, list):
                self.available_colors = self.options.color_palette
            else:
                print("Warning: color_palette must be a list of RGBColor objects. Using default colors.")
                self.available_colors = [color.value for color in Colors if color != Colors.BLACK]
        else:
            # Use all colors except black
            self.available_colors = [color.value for color in Colors if color != Colors.BLACK]
    
    def loop(self):
        """Execute one iteration of the random colors effect."""
        if self.options.per_device:
            self._random_per_device()
        else:
            self._random_all_devices()
    
    def _random_per_device(self):
        """Set each device to a random color."""
        devices = self.get_target_devices()
        for device in devices:
            if hasattr(device, 'set_color'):
                color = random.choice(self.available_colors)
                self.set_devices_color([device], color)
    
    def _random_all_devices(self):
        """Set all devices to the same random color."""
        color = random.choice(self.available_colors)
        self.set_all_target_devices_color(color)
    
    def stop(self):
        """Clean up the effect."""
        print("Stopping random colors effect...")
        self.turn_off_target_devices() 