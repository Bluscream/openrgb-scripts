"""
Police lights effect - alternating blue and red flashes.
"""

import time
from classes import Effect, EffectOptions, Colors


class PoliceLightsOptions(EffectOptions):
    """
    Options for police lights effect.
    """
    
    def __init__(self, 
                 sleep_s: float = 0.1,
                 devices: list = None,
                 max_brightness: float = 1.0,
                 flash_duration_ms: int = 100,
                 pause_duration_s: float = 0.5):
        """
        Initialize police lights options.
        
        Args:
            flash_duration_ms: Duration of each flash in milliseconds
            pause_duration_s: Duration of pause between color changes
        """
        super().__init__(sleep_s, devices, max_brightness)
        self.flash_duration_ms = flash_duration_ms
        self.pause_duration_s = pause_duration_s


class PoliceLightsEffect(Effect):
    """
    Police lights effect - alternating blue and red flashes.
    """
    
    def __init__(self, client, options: PoliceLightsOptions):
        super().__init__(client, options)
        self.current_color = "blue"
        self.flash_count = 0
    
    def start(self):
        """Initialize the effect."""
        print("Starting police lights effect...")
        self.current_color = "blue"
        self.flash_count = 0
    
    def loop(self):
        """Execute one iteration of the police lights pattern."""
        # Flash blue twice
        for _ in range(2):
            self.set_all_target_devices_color(Colors.BLUE.value)
            time.sleep(self.options.flash_duration_ms / 1000.0)
            self.turn_off_target_devices()
            time.sleep(0.05)  # Small pause between flashes
        
        # Pause
        time.sleep(self.options.pause_duration_s)
        
        # Flash red twice
        for _ in range(2):
            self.set_all_target_devices_color(Colors.RED.value)
            time.sleep(self.options.flash_duration_ms / 1000.0)
            self.turn_off_target_devices()
            time.sleep(0.05)  # Small pause between flashes
        
        # Pause
        time.sleep(self.options.pause_duration_s)
    
    def stop(self):
        """Clean up the effect."""
        print("Stopping police lights effect...")
        self.turn_off_target_devices() 