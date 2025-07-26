#!/usr/bin/env python3
"""
Audio Effect Example

This script demonstrates how to use the audio effect to listen to the default
output device and flash OpenRGB devices in random colors when audio peaks are detected.
"""

import sys
import time
from openrgb import OpenRGBClient
from effects.audio import AudioEffect, AudioOptions

def main():
    """Main function to run the audio effect example."""
    
    # Connect to OpenRGB server
    try:
        client = OpenRGBClient()
        print(f"Connected to OpenRGB server")
        print(f"Found {len(client.devices)} devices:")
        for i, device in enumerate(client.devices):
            print(f"  {i}: {device.name}")
    except Exception as e:
        print(f"Error connecting to OpenRGB server: {e}")
        print("Make sure OpenRGB server is running (openrgb --server)")
        return
    
    # Create audio effect options
    options = AudioOptions(
        sleep_s=0.01,              # Update rate (10ms)
        devices=None,              # Use all devices (or specify device indices)
        max_brightness=0.8,        # 80% brightness
        sample_rate=44100,         # Audio sample rate
        chunk_size=1024,           # Audio chunk size
        peak_threshold=0.05,       # Audio peak threshold (adjust based on your audio)
        peak_duration=0.1,         # How long to flash when peak detected
        fade_duration=0.3,         # How long to fade out
        audio_device_index=None    # Use default audio device
    )
    
    # Create and run the audio effect
    effect = AudioEffect(client, options)
    
    print("\nAudio Effect Started!")
    print("The devices will flash in random colors when audio peaks are detected.")
    print("Press Ctrl+C to stop the effect.")
    print("\nTips:")
    print("- Adjust 'peak_threshold' if the effect is too sensitive or not sensitive enough")
    print("- Adjust 'peak_duration' and 'fade_duration' to change the flash timing")
    print("- Make sure you have audio playing to see the effect")
    
    try:
        effect.run()
    except KeyboardInterrupt:
        print("\nStopping audio effect...")
    finally:
        effect.stop()
        print("Audio effect stopped.")

if __name__ == "__main__":
    main() 