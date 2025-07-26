#!/usr/bin/env python3
"""
Test script for the Desktop effect.

This script demonstrates how to use the Desktop effect to capture screenshots
and set device colors based on the dominant color on screen.
"""

import sys
import time
from classes import OpenRGBController
from effects.desktop import DesktopEffect, DesktopOptions


def test_desktop_effect():
    """Test the desktop effect with different configurations."""
    
    # Initialize controller
    controller = OpenRGBController()
    
    if not controller.connect():
        print("Failed to connect to OpenRGB server. Make sure OpenRGB is running with --server flag.")
        return False
    
    print("Testing Desktop Effect...")
    print("This effect will capture screenshots and set device colors based on screen content.")
    print("Press Ctrl+C to stop the test.")
    
    try:
        # Test 1: Basic desktop effect with dominant color sampling
        print("\n=== Test 1: Basic Desktop Effect (Dominant Color) ===")
        options = DesktopOptions(
            sleep_s=0.1,  # 100ms between captures
            capture_interval_ms=100,
            color_sampling="dominant",
            color_tolerance=30,
            smooth_transitions=True,
            transition_duration_ms=200
        )
        
        effect = DesktopEffect(controller.client, options)
        print("Starting basic desktop effect...")
        effect.run()
        
    except KeyboardInterrupt:
        print("\nTest stopped by user")
    except Exception as e:
        print(f"Error during test: {e}")
        return False
    finally:
        controller.turn_off_all_lights()
    
    return True


def test_desktop_effect_average():
    """Test the desktop effect with average color sampling."""
    
    # Initialize controller
    controller = OpenRGBController()
    
    if not controller.connect():
        print("Failed to connect to OpenRGB server. Make sure OpenRGB is running with --server flag.")
        return False
    
    print("Testing Desktop Effect with Average Color Sampling...")
    print("This will use the average color of the entire screen.")
    print("Press Ctrl+C to stop the test.")
    
    try:
        # Test 2: Desktop effect with average color sampling
        print("\n=== Test 2: Desktop Effect (Average Color) ===")
        options = DesktopOptions(
            sleep_s=0.1,
            capture_interval_ms=100,
            color_sampling="average",
            smooth_transitions=True,
            transition_duration_ms=300
        )
        
        effect = DesktopEffect(controller.client, options)
        print("Starting average color desktop effect...")
        effect.run()
        
    except KeyboardInterrupt:
        print("\nTest stopped by user")
    except Exception as e:
        print(f"Error during test: {e}")
        return False
    finally:
        controller.turn_off_all_lights()
    
    return True


def main():
    """Main function to run desktop effect tests."""
    print("Desktop Effect Test Suite")
    print("========================")
    
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        
        if test_type == "average":
            success = test_desktop_effect_average()
        else:
            print(f"Unknown test type: {test_type}")
            print("Available tests: average")
            return False
    else:
        # Default to basic test
        success = test_desktop_effect()
    
    if success:
        print("\nTest completed successfully!")
    else:
        print("\nTest failed!")
        return False
    
    return True


if __name__ == "__main__":
    main() 