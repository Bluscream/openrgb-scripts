"""
Rainbow effects - cycling through rainbow colors.
"""

import time
from classes import Effect, EffectOptions, Colors, RAINBOW_COLORS, lerp_color


class RainbowOptions(EffectOptions):
    """
    Options for rainbow effects.
    """
    
    def __init__(self, 
                 sleep_s: float = 0.2,
                 devices: list = None,
                 max_brightness: float = 1.0,
                 smooth_transition: bool = True,
                 steps_per_color: int = 30,
                 transition_delay: float = 0.03):
        """
        Initialize rainbow options.
        
        Args:
            smooth_transition: Whether to use smooth color transitions
            steps_per_color: Number of steps between each color (for smooth mode)
            transition_delay: Delay between steps in seconds (for smooth mode)
        """
        super().__init__(sleep_s, devices, max_brightness)
        self.smooth_transition = smooth_transition
        self.steps_per_color = steps_per_color
        self.transition_delay = transition_delay


class RainbowEffect(Effect):
    """
    Rainbow effect - cycling through rainbow colors.
    """
    
    def __init__(self, client, options: RainbowOptions):
        super().__init__(client, options)
        self.current_color_index = 0
        self.current_step = 0
    
    def start(self):
        """Initialize the effect."""
        print("Starting rainbow effect...")
        self.current_color_index = 0
        self.current_step = 0
    
    def loop(self):
        """Execute one iteration of the rainbow effect."""
        if self.options.smooth_transition:
            self._smooth_rainbow_step()
        else:
            self._discrete_rainbow_step()
    
    def _discrete_rainbow_step(self):
        """Execute one step of discrete rainbow effect."""
        color = RAINBOW_COLORS[self.current_color_index]
        self.set_all_target_devices_color(color)
        self.current_color_index = (self.current_color_index + 1) % len(RAINBOW_COLORS)
    
    def _smooth_rainbow_step(self):
        """Execute one step of smooth rainbow effect."""
        # Get current and next colors
        c1 = RAINBOW_COLORS[self.current_color_index]
        c2 = RAINBOW_COLORS[(self.current_color_index + 1) % len(RAINBOW_COLORS)]
        
        # Calculate interpolation factor
        t = self.current_step / self.options.steps_per_color
        color = lerp_color(c1, c2, t)
        
        # Set the interpolated color
        self.set_all_target_devices_color(color)
        
        # Update step counter
        self.current_step += 1
        if self.current_step >= self.options.steps_per_color:
            self.current_step = 0
            self.current_color_index = (self.current_color_index + 1) % len(RAINBOW_COLORS)
    
    def stop(self):
        """Clean up the effect."""
        print("Stopping rainbow effect...")
        self.turn_off_target_devices() 