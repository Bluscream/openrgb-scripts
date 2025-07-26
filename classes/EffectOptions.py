"""
EffectOptions class for configuring OpenRGB effects.
"""

from typing import List, Optional


class EffectOptions:
    """
    Configuration options for effects.
    """
    
    def __init__(self, 
                 sleep_s: float = 0.1,
                 devices: Optional[List[int]] = None,
                 max_brightness: float = 1.0,
                 **kwargs):
        """
        Initialize effect options.
        
        Args:
            sleep_s: Sleep time between iterations in seconds
            devices: List of device indices to target (None or empty for all devices)
            max_brightness: Brightness multiplier (0.0 to 1.0)
            **kwargs: Additional effect-specific options
        """
        self.sleep_s = sleep_s
        self.devices = devices
        self.max_brightness = max_brightness
        
        # Store additional options
        for key, value in kwargs.items():
            setattr(self, key, value) 