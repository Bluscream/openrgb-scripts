"""
Lightning effect - simulates lightning strikes with bright flashes and fade-out.
"""

import time
import random
from classes import Effect, EffectOptions, Colors, lerp_color


class LightningOptions(EffectOptions):
    """
    Options for lightning effect.
    """
    
    def __init__(self, 
                 sleep_s: float = 0.5,
                 devices: list = None,
                 max_brightness: float = 1.0,
                 color: str = "white",
                 target_mode: str = "random",
                 fade_min_ms: int = 100,
                 fade_max_ms: int = 500,
                 flash_duration_ms: int = 50):
        """
        Initialize lightning options.
        
        Args:
            color: "random" or specific color name (e.g., "white", "blue", "yellow")
            target_mode: "random" (one random device) or "all" (all target devices)
            fade_min_ms: Minimum fade-out duration in milliseconds
            fade_max_ms: Maximum fade-out duration in milliseconds
            flash_duration_ms: Duration of the bright flash in milliseconds
        """
        super().__init__(sleep_s, devices, max_brightness)
        self.color = color
        self.target_mode = target_mode
        self.fade_min_ms = fade_min_ms
        self.fade_max_ms = fade_max_ms
        self.flash_duration_ms = flash_duration_ms


class LightningEffect(Effect):
    """
    Lightning effect - simulates lightning strikes with bright flashes and fade-out.
    
    This effect creates realistic lightning by:
    1. Flash: Bright flash at 100% brightness
    2. Fade: Gradual fade-out over random duration
    3. Repeat: After sleep interval
    """
    
    def __init__(self, client, options: LightningOptions):
        super().__init__(client, options)
        self.flash_color = None
        self.target_devices = []
        
        # Color mapping for string input
        self.color_map = {
            "white": Colors.WHITE.value,
            "blue": Colors.BLUE.value,
            "yellow": Colors.YELLOW.value,
            "cyan": Colors.CYAN.value,
            "light_blue": Colors.LIGHT_BLUE.value,
            "orange": Colors.ORANGE.value,
            "red": Colors.RED.value,
            "green": Colors.GREEN.value,
            "magenta": Colors.MAGENTA.value,
            "pink": Colors.PINK.value,
            "violet": Colors.VIOLET.value,
            "indigo": Colors.INDIGO.value,
        }
    
    def start(self):
        """Initialize the effect."""
        print("Starting lightning effect...")
        self._select_flash_color()
        self._select_target_devices()
    
    def _select_flash_color(self):
        """Select the color for the lightning flash."""
        if self.options.color.lower() == "random":
            # Random color from available colors (excluding black)
            available_colors = [color.value for color in Colors if color != Colors.BLACK]
            self.flash_color = random.choice(available_colors)
        else:
            # Use specified color
            color_name = self.options.color.lower()
            if color_name in self.color_map:
                self.flash_color = self.color_map[color_name]
            else:
                print(f"Warning: Unknown color '{self.options.color}'. Using white.")
                self.flash_color = Colors.WHITE.value
    
    def _select_target_devices(self):
        """Select which devices to target for this lightning strike."""
        all_target_devices = self.get_target_devices()
        
        if self.options.target_mode.lower() == "random":
            # Select one random device
            if all_target_devices:
                self.target_devices = [random.choice(all_target_devices)]
            else:
                self.target_devices = []
        else:
            # Use all target devices
            self.target_devices = all_target_devices
    
    def loop(self):
        """Execute one complete lightning strike cycle."""
        if not self.target_devices:
            return
        
        # Select new color and target devices for this strike
        self._select_flash_color()
        self._select_target_devices()
        
        if not self.target_devices:
            return
        
        # Phase 1: Bright flash
        for device in self.target_devices:
            if hasattr(device, 'set_color'):
                # Use full brightness for the flash (ignore max_brightness setting)
                device.set_color(self.flash_color)
        
        # Hold the flash for the specified duration
        time.sleep(self.options.flash_duration_ms / 1000.0)
        
        # Phase 2: Fade out over random duration
        fade_duration = random.randint(self.options.fade_min_ms, self.options.fade_max_ms) / 1000.0
        fade_start = time.time()
        
        while True:
            elapsed = time.time() - fade_start
            progress = min(elapsed / fade_duration, 1.0)
            
            # Interpolate from flash color to black
            faded_color = lerp_color(self.flash_color, Colors.BLACK.value, progress)
            
            # Apply brightness clamping to the faded color
            faded_color = self.clamp_brightness(faded_color)
            
            # Set devices to faded color
            for device in self.target_devices:
                if hasattr(device, 'set_color'):
                    device.set_color(faded_color)
            
            # Check if fade is complete
            if progress >= 1.0:
                break
            
            # Small delay for smooth fade animation
            time.sleep(0.01)  # 10ms delay for smooth animation
    
    def stop(self):
        """Clean up the effect."""
        print("Stopping lightning effect...")
        self.turn_off_target_devices() 