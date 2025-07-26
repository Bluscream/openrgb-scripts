#!/usr/bin/env python3
"""
OpenRGB Light Flashing Script

This script connects to the OpenRGB server and provides various RGB lighting effects
including flashing patterns, rainbow effects, and police lights.
"""

import time
import sys
from openrgb import OpenRGBClient
from openrgb.utils import RGBColor, DeviceType


class OpenRGBController:
    """
    A class to control OpenRGB devices with various lighting effects.
    """
    
    def __init__(self, max_brightness=0.5, duration_ms=150):
        """
        Initialize the OpenRGB controller.
        
        Args:
            max_brightness (float): Brightness multiplier (0.0 to 1.0)
            duration_ms (int): Default flash duration in milliseconds
        """
        self.max_brightness = max_brightness
        self.duration_ms = duration_ms
        self.client = None
        
        # Define color palette
        self.colors = {
            "red": RGBColor(255, 0, 0),
            "orange": RGBColor(255, 127, 0),
            "yellow": RGBColor(255, 255, 0),
            "green": RGBColor(0, 255, 0),
            "blue": RGBColor(0, 0, 255),
            "indigo": RGBColor(75, 0, 130),
            "violet": RGBColor(148, 0, 211),
            "white": RGBColor(255, 255, 255),
            "black": RGBColor(0, 0, 0),
            "cyan": RGBColor(0, 255, 255),
            "magenta": RGBColor(255, 0, 255),
            "pink": RGBColor(255, 192, 203),
            "brown": RGBColor(165, 42, 42),
            "gray": RGBColor(128, 128, 128),
            "light_gray": RGBColor(211, 211, 211),
            "dark_gray": RGBColor(169, 169, 169),
            "light_blue": RGBColor(173, 216, 230),
        }
        
        # Rainbow color sequence
        self.rainbow_colors = [
            self.colors["red"],
            self.colors["orange"],
            self.colors["yellow"],
            self.colors["green"],
            self.colors["blue"],
            self.colors["indigo"],
            self.colors["violet"],
        ]
    
    def connect(self):
        """
        Connect to the OpenRGB server.
        
        Raises:
            ConnectionRefusedError: If unable to connect to OpenRGB server
        """
        print("Connecting to OpenRGB server...")
        self.client = OpenRGBClient()
        print(f"Connected! Found {len(self.client.devices)} devices:")
        for i, device in enumerate(self.client.devices):
            print(f"  {i+1}. {device.name} ({device.type})")
    
    def clamp_brightness(self, color):
        """
        Clamp the brightness of an RGBColor object based on max_brightness.
        
        Args:
            color: RGBColor object
            
        Returns:
            RGBColor object with clamped brightness
        """
        r = int(color.red * self.max_brightness)
        g = int(color.green * self.max_brightness)
        b = int(color.blue * self.max_brightness)
        return RGBColor(r, g, b)
    
    def set_all_devices_color(self, color):
        """
        Set all devices to the specified color.
        
        Args:
            color: RGBColor object
        """
        if self.client is None:
            raise RuntimeError("Not connected to OpenRGB server. Call connect() first.")
        
        for device in self.client.devices:
            if hasattr(device, 'set_color'):
                device.set_color(color)
    
    def flash_lights(self, color, duration_ms=None, count=1):
        """
        Flash all RGB devices with the specified color.
        
        Args:
            color: RGBColor object
            duration_ms: Duration of each flash in milliseconds (uses default if None)
            count: Number of flashes
        """
        if duration_ms is None:
            duration_ms = self.duration_ms
            
        for i in range(count):
            # Apply brightness clamping to the color
            clamped_color = self.clamp_brightness(color)
            print(f"Flash {i+1}/{count}: Setting all devices to {clamped_color}")
            
            # Set all devices to the specified color
            self.set_all_devices_color(clamped_color)
            
            # Wait for the specified duration
            time.sleep(duration_ms / 1000.0)
            
            # Turn off all lights (black color)
            self.set_all_devices_color(self.colors["black"])
            
            # Small pause between flashes (if multiple)
            if i < count - 1:
                time.sleep(0.05)  # 50ms pause between flashes
    
    def police_lights(self, duration_ms=150, sleep_s=0.5):
        """
        Execute police light pattern: 2x blue, 500ms pause, 2x red, 500ms pause
        """
        self.flash_lights(self.colors["blue"], duration_ms, count=2)
        time.sleep(sleep_s)
        self.flash_lights(self.colors["red"], duration_ms, count=2)
        time.sleep(sleep_s)
    
    def rainbow(self, sleep_s=0.2):
        """
        Cycle through a rainbow of colors on all RGB devices.
        """
        for color in self.rainbow_colors:
            # Apply brightness clamping to the color
            clamped_color = self.clamp_brightness(color)
            print(f"Setting all devices to {clamped_color}")
            self.set_all_devices_color(clamped_color)
            time.sleep(sleep_s)
    
    def rainbow_smooth(self, steps_per_color=30, sleep_s=0.03):
        """
        Smoothly transition through a rainbow of colors on all RGB devices.
        """

        def lerp_color(c1, c2, t):
            """Linearly interpolate between two RGBColor objects."""
            r = int(c1.red + (c2.red - c1.red) * t)
            g = int(c1.green + (c2.green - c1.green) * t)
            b = int(c1.blue + (c2.blue - c1.blue) * t)
            return RGBColor(r, g, b)

        for i in range(len(self.rainbow_colors)):
            c1 = self.rainbow_colors[i]
            c2 = self.rainbow_colors[(i + 1) % len(self.rainbow_colors)]
            for step in range(steps_per_color):
                t = step / steps_per_color
                color = lerp_color(c1, c2, t)
                # Apply brightness clamping to the interpolated color
                clamped_color = self.clamp_brightness(color)
                self.set_all_devices_color(clamped_color)
                time.sleep(sleep_s)
    
    def turn_off_all_lights(self):
        """
        Turn off all RGB devices (set to black).
        """
        self.set_all_devices_color(self.colors["black"])
    
    def run_pattern_loop(self, pattern):
        """
        Run the police light pattern in a continuous loop until Ctrl+C is pressed.
        """
        try:
            print("Press Ctrl+C to stop the loop")
            
            cycle_count = 0
            
            while True:
                cycle_count += 1
                match pattern:
                    case "police":
                        self.police_lights(duration_ms=150, sleep_s=0.5)
                    case "rainbow":
                        self.rainbow(sleep_s=0.2)
                    case "rainbow_smooth":
                        self.rainbow_smooth(steps_per_color=30, sleep_s=0.03)
                time.sleep(.01)
                
        except KeyboardInterrupt:
            print(f"\n\nStopped by user after {cycle_count} cycles.")
            print("Turning off all lights...")
            self.turn_off_all_lights()
            print("All lights turned off. Goodbye!")


def main():
    """Main function to demonstrate the OpenRGBController class."""
    try:
        # Create and configure the controller
        controller = OpenRGBController(max_brightness=0.3, duration_ms=150)
        
        # Connect to OpenRGB server
        controller.connect()
        
        # Run the rainbow effect loop
        controller.run_pattern_loop("rainbow_smooth")
        
    except ConnectionRefusedError:
        print("Error: Could not connect to OpenRGB server.")
        print("Make sure OpenRGB is running and the server is enabled.")
        print("You can start OpenRGB with: openrgb --server")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 