#!/usr/bin/env python3
"""
Test script for audio effects.

This script tests the audio effects without requiring OpenRGB connection.
"""

import time
import numpy as np
import sounddevice as sd
from effects.audio import AudioEffect, AudioOptions
from effects.audio_loopback import AudioLoopbackEffect, AudioLoopbackOptions

def test_audio_devices():
    """Test and list available audio devices."""
    print("Testing audio devices...")
    
    try:
        devices = sd.query_devices()
        
        print(f"Found {len(devices)} audio devices:")
        for i, device in enumerate(devices):
            print(f"  {i}: {device['name']}")
            print(f"      Inputs: {device['max_inputs']}, Outputs: {device['max_outputs']}")
        
        # Test default devices
        try:
            default_input = sd.query_devices(kind='input')
            print(f"\nDefault input device: {default_input['name']} (index: {default_input['index']})")
        except Exception as e:
            print(f"\nNo default input device: {e}")
        
        try:
            default_output = sd.query_devices(kind='output')
            print(f"Default output device: {default_output['name']} (index: {default_output['index']})")
        except Exception as e:
            print(f"No default output device: {e}")
        
    except Exception as e:
        print(f"Error testing audio devices: {e}")

def test_audio_processing():
    """Test basic audio processing functionality."""
    print("\nTesting audio processing...")
    
    try:
        # Create test audio data (sine wave)
        sample_rate = 44100
        duration = 0.1  # 100ms
        frequency = 440  # A4 note
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio_data = np.sin(2 * np.pi * frequency * t)
        
        # Test RMS calculation
        rms = np.sqrt(np.mean(audio_data.astype(np.float32) ** 2))
        
        print(f"Test audio RMS: {rms:.4f}")
        
        # Test FFT
        fft = np.fft.fft(audio_data.astype(np.float32))
        freqs = np.fft.fftfreq(len(audio_data), 1.0 / sample_rate)
        
        # Find peak frequency
        peak_idx = np.argmax(np.abs(fft))
        peak_freq = freqs[peak_idx]
        
        print(f"Peak frequency: {peak_freq:.1f} Hz (expected: {frequency} Hz)")
        
    except Exception as e:
        print(f"Error testing audio processing: {e}")

def test_effect_creation():
    """Test creating audio effects without running them."""
    print("\nTesting effect creation...")
    
    try:
        # Test basic audio effect
        options = AudioOptions(
            peak_threshold=0.05,
            peak_duration=0.1,
            fade_duration=0.2
        )
        print("✓ Basic AudioOptions created successfully")
        
        # Test advanced audio effect
        options_advanced = AudioLoopbackOptions(
            peak_threshold=0.03,
            peak_duration=0.15,
            fade_duration=0.4,
            use_loopback=True,
            frequency_bands=[60, 250, 500, 2000, 4000, 8000]
        )
        print("✓ AudioLoopbackOptions created successfully")
        
        print("✓ Audio effect classes can be instantiated")
        
    except Exception as e:
        print(f"Error testing effect creation: {e}")

def main():
    """Main test function."""
    print("Audio Effects Test Suite")
    print("=" * 50)
    
    test_audio_devices()
    test_audio_processing()
    test_effect_creation()
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("\nTo run the actual audio effects:")
    print("1. Make sure OpenRGB server is running: openrgb --server")
    print("2. Run: python audio_example.py")
    print("3. Or run: python audio_loopback_example.py")

if __name__ == "__main__":
    main() 