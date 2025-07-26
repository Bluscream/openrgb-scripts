#!/usr/bin/env python3
"""
Advanced Audio Loopback Effect Example

This script demonstrates how to use the advanced audio loopback effect to listen to
system audio output and flash OpenRGB devices with frequency-based colors when audio peaks are detected.
"""

import sys
import time
from openrgb import OpenRGBClient
from effects.audio_loopback import AudioLoopbackEffect, AudioLoopbackOptions

def main():
    """Main function to run the advanced audio loopback effect example."""
    
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
    
    # Create advanced audio loopback effect options
    options = AudioLoopbackOptions(
        sleep_s=0.01,              # Update rate (10ms)
        devices=None,              # Use all devices (or specify device indices)
        max_brightness=0.8,        # 80% brightness
        sample_rate=44100,         # Audio sample rate
        chunk_size=1024,           # Audio chunk size
        peak_threshold=0.03,       # Audio peak threshold (adjust based on your audio)
        peak_duration=0.15,        # How long to flash when peak detected
        fade_duration=0.4,         # How long to fade out
        audio_device_index=None,   # Use default audio device
        use_loopback=True,         # Try to use loopback recording
        frequency_bands=[60, 250, 500, 2000, 4000, 8000]  # Frequency bands to analyze
    )
    
    # Create and run the audio loopback effect
    effect = AudioLoopbackEffect(client, options)
    
    print("\nAdvanced Audio Loopback Effect Started!")
    print("The devices will flash with frequency-based colors when audio peaks are detected.")
    print("Press Ctrl+C to stop the effect.")
    print("\nFrequency Color Mapping:")
    print("- Red: Bass (60-250 Hz)")
    print("- Orange: Mid Bass (250-500 Hz)")
    print("- Yellow: Low Mid (500-2000 Hz)")
    print("- Green: Mid (2000-4000 Hz)")
    print("- Cyan: High Mid (4000-8000 Hz)")
    print("- Purple: High (8000+ Hz)")
    print("\nTips:")
    print("- Adjust 'peak_threshold' if the effect is too sensitive or not sensitive enough")
    print("- Adjust 'peak_duration' and 'fade_duration' to change the flash timing")
    print("- Make sure you have audio playing to see the effect")
    print("- If loopback doesn't work, try setting use_loopback=False")
    print("- Enable 'Stereo Mix' in Windows sound settings for better loopback support")
    
    try:
        effect.run()
    except KeyboardInterrupt:
        print("\nStopping audio loopback effect...")
    finally:
        effect.stop()
        print("Audio loopback effect stopped.")

if __name__ == "__main__":
    main() 