"""
Breathing effect - smoothly fades a color in and out to create a breathing effect.
"""

import math
import time
from classes import Effect, EffectOptions, Colors, parse_color
from openrgb.utils import RGBColor


class BreathingOptions(EffectOptions):
    """
    Options for breathing effect.
    """
    
    def __init__(self, 
                 sleep_s: float = 0.05,
                 devices: list = None,
                 max_brightness: float = 1.0,
                 color: str = "white",
                 breathing_speed: float = 2.0,
                 min_brightness: float = 0.1):
        """
        Initialize breathing options.
        
        Args:
            color: Color to breathe (can be 'random', a color name like 'red', 'blue', etc., RGB values like '255,0,0', or hex codes like '#FF0000')
            breathing_speed: Speed of the breathing effect in cycles per second
            min_brightness: Minimum brightness during breathing (0.0 to 1.0)
        """
        super().__init__(sleep_s, devices, max_brightness)
        self.color = color
        self.breathing_speed = breathing_speed
        self.min_brightness = min_brightness


class BreathingEffect(Effect):
    """
    Breathing effect - smoothly fades a color in and out to create a breathing effect.
    """
    
    def __init__(self, client, options: BreathingOptions):
        super().__init__(client, options)
        self.base_color = None
        self.start_time = None
    
    def _parse_color(self, color_str: str) -> RGBColor:
        """
        Parse color string into RGBColor object.
        
        Args:
            color_str: Color string (e.g., 'red', '255,0,0', '#FF0000', 'random')
            
        Returns:
            RGBColor object
        """
        return parse_color(color_str)
    
    def start(self):
        """Initialize the effect."""
        print(f"Starting breathing effect with color: {self.options.color}, speed: {self.options.breathing_speed} cycles/s")
        self.base_color = self._parse_color(self.options.color)
        self.start_time = time.time()
    
    def loop(self):
        """Execute one iteration of the breathing effect."""
        # Calculate time elapsed since start
        elapsed_time = time.time() - self.start_time
        
        # Calculate breathing factor using sine wave (0 to 1)
        # The sine wave goes from -1 to 1, so we shift and scale it to 0 to 1
        breathing_factor = (math.sin(2 * math.pi * self.options.breathing_speed * elapsed_time) + 1) / 2
        
        # Apply min_brightness offset and scale
        # breathing_factor goes from 0 to 1, we want it to go from min_brightness to 1
        brightness = self.options.min_brightness + (1 - self.options.min_brightness) * breathing_factor
        
        # Apply the breathing brightness to the base color
        r = max(0, min(255, int(self.base_color.red * brightness * self.options.max_brightness)))
        g = max(0, min(255, int(self.base_color.green * brightness * self.options.max_brightness)))
        b = max(0, min(255, int(self.base_color.blue * brightness * self.options.max_brightness)))
        
        breathing_color = RGBColor(r, g, b)
        self.set_all_target_devices_color(breathing_color)
    
    def stop(self):
        """Clean up the effect."""
        print("Stopping breathing effect...")
        # Don't turn off devices when stopping breathing effect
        # This allows the current color to persist 