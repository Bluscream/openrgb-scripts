#!/usr/bin/env python3
"""
OpenRGB Light Flashing Script

This script connects to the OpenRGB server and flashes all RGB devices
in the following pattern:
- 2x blue flashes (100ms each)
- 500ms pause
- 2x red flashes (100ms each)
- 500ms pause
"""

import time
import sys
from openrgb import OpenRGBClient
from openrgb.utils import RGBColor, DeviceType

colors = {
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
rainbow_colors = [
    colors["red"],
    colors["orange"],
    colors["yellow"],
    colors["green"],
    colors["blue"],
    colors["indigo"],
    colors["violet"],
]

def flash_lights(client, color, duration_ms=100, count=1):
    """
    Flash all RGB devices with the specified color.
    
    Args:
        client: OpenRGB client instance
        color: RGBColor object
        duration_ms: Duration of each flash in milliseconds
        count: Number of flashes
    """
    for i in range(count):
        # Apply brightness clamping to the color
        clamped_color = clamp_brightness(color)
        print(f"Flash {i+1}/{count}: Setting all devices to {clamped_color}")
        
        # Set all devices to the specified color
        for device in client.devices:
            if hasattr(device, 'set_color'):
                device.set_color(clamped_color)
        
        # Wait for the specified duration
        time.sleep(duration_ms / 1000.0)
        
        # Turn off all lights (black color)
        for device in client.devices:
            if hasattr(device, 'set_color'):
                device.set_color(colors["black"])
        
        # Small pause between flashes (if multiple)
        if i < count - 1:
            time.sleep(0.05)  # 50ms pause between flashes

def police():
    flash_lights(client, colors["blue"], duration_ms, count=2)
    time.sleep(0.5)
    flash_lights(client, colors["red"], duration_ms, count=2) 
    time.sleep(0.5)

def rainbow():
    """
    Cycle through a rainbow of colors on all RGB devices.
    """
    for color in rainbow_colors:
        # Apply brightness clamping to the color
        clamped_color = clamp_brightness(color)
        print(f"Setting all devices to {clamped_color}")
        for device in client.devices:
            if hasattr(device, 'set_color'):
                device.set_color(clamped_color)
        time.sleep(0.2)

def rainbow_smooth():
    """
    Smoothly transition through a rainbow of colors on all RGB devices.
    """
    steps_per_color = 30  # Number of steps between each color
    transition_delay = 0.03  # Delay between steps in seconds

    def lerp_color(c1, c2, t):
        """Linearly interpolate between two RGBColor objects."""
        r = int(c1.red + (c2.red - c1.red) * t)
        g = int(c1.green + (c2.green - c1.green) * t)
        b = int(c1.blue + (c2.blue - c1.blue) * t)
        return RGBColor(r, g, b)

    for i in range(len(rainbow_colors)):
        c1 = rainbow_colors[i]
        c2 = rainbow_colors[(i + 1) % len(rainbow_colors)]
        for step in range(steps_per_color):
            t = step / steps_per_color
            color = lerp_color(c1, c2, t)
            # Apply brightness clamping to the interpolated color
            clamped_color = clamp_brightness(color)
            for device in client.devices:
                if hasattr(device, 'set_color'):
                    device.set_color(clamped_color)
            time.sleep(transition_delay)

# Connect to OpenRGB server
print("Connecting to OpenRGB server...")
client = OpenRGBClient()
duration_ms = 150
max_brightness = 0.5  # Adjust this value to control overall brightness

def clamp_brightness(color):
    """
    Clamp the brightness of an RGBColor object based on max_brightness.
    
    Args:
        color: RGBColor object
        
    Returns:
        RGBColor object with clamped brightness
    """
    r = int(color.red * max_brightness)
    g = int(color.green * max_brightness)
    b = int(color.blue * max_brightness)
    return RGBColor(r, g, b)

def main():
    """Main function to execute the light flashing pattern in a continuous loop."""
    try:
        
        # Get device information
        print(f"Connected! Found {len(client.devices)} devices:")
        for i, device in enumerate(client.devices):
            print(f"  {i+1}. {device.name} ({device.type})")
        
        print("\nStarting light flashing pattern in continuous loop...")
        print("Press Ctrl+C to stop the loop")
        
        cycle_count = 0
        
        try:
            while True:
                cycle_count += 1
                # print(f"\n--- Cycle {cycle_count} ---")
                rainbow_smooth()
                
        except KeyboardInterrupt:
            print(f"\n\nStopped by user after {cycle_count} cycles.")
            print("Turning off all lights...")
            
            # Turn off all lights before exiting
            black = RGBColor(0, 0, 0)
            for device in client.devices:
                if hasattr(device, 'set_color'):
                    device.set_color(black)
            
            print("All lights turned off. Goodbye!")
        
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