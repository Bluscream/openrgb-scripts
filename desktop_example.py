#!/usr/bin/env python3
"""
Desktop Effect Example

This script demonstrates how to use the Desktop effect programmatically
to capture screenshots and set device colors based on screen content.
"""

import time
from classes import OpenRGBController
from effects.desktop import DesktopEffect, DesktopOptions


def example_dominant_color():
    """Example using dominant color sampling."""
    print("=== Desktop Effect - Dominant Color Example ===")
    
    # Initialize controller
    controller = OpenRGBController()
    
    if not controller.connect():
        print("Failed to connect to OpenRGB server")
        return
    
    # Configure options for dominant color sampling
    options = DesktopOptions(
        sleep_s=0.1,                    # 100ms between captures
        capture_interval_ms=100,        # Capture every 100ms
        color_sampling="dominant",      # Use most common color
        color_tolerance=30,             # Group similar colors
        smooth_transitions=True,        # Smooth color changes
        transition_duration_ms=200,     # 200ms transition time
        max_brightness=0.8              # 80% brightness
    )
    
    # Create and run the effect
    effect = DesktopEffect(controller.client, options)
    
    try:
        print("Starting desktop effect with dominant color sampling...")
        print("This will find the most common color on your screen and set devices to that color.")
        print("Press Ctrl+C to stop.")
        
        effect.run()
        
    except KeyboardInterrupt:
        print("\nStopping desktop effect...")
    finally:
        effect.stop()
        controller.turn_off_all_lights()


def example_average_color():
    """Example using average color sampling."""
    print("=== Desktop Effect - Average Color Example ===")
    
    # Initialize controller
    controller = OpenRGBController()
    
    if not controller.connect():
        print("Failed to connect to OpenRGB server")
        return
    
    # Configure options for average color sampling
    options = DesktopOptions(
        sleep_s=0.05,                   # 50ms between captures (faster)
        capture_interval_ms=50,         # Capture every 50ms
        color_sampling="average",       # Use average color
        smooth_transitions=True,        # Smooth color changes
        transition_duration_ms=150,     # 150ms transition time
        max_brightness=0.9              # 90% brightness
    )
    
    # Create and run the effect
    effect = DesktopEffect(controller.client, options)
    
    try:
        print("Starting desktop effect with average color sampling...")
        print("This will calculate the average color of your entire screen.")
        print("Press Ctrl+C to stop.")
        
        effect.run()
        
    except KeyboardInterrupt:
        print("\nStopping desktop effect...")
    finally:
        effect.stop()
        controller.turn_off_all_lights()


def example_immediate_transitions():
    """Example with immediate color transitions (no smoothing)."""
    print("=== Desktop Effect - Immediate Transitions Example ===")
    
    # Initialize controller
    controller = OpenRGBController()
    
    if not controller.connect():
        print("Failed to connect to OpenRGB server")
        return
    
    # Configure options for immediate transitions
    options = DesktopOptions(
        sleep_s=0.2,                    # 200ms between captures
        capture_interval_ms=200,        # Capture every 200ms
        color_sampling="dominant",      # Use most common color
        color_tolerance=50,             # Higher tolerance for more grouping
        smooth_transitions=False,       # No smooth transitions
        max_brightness=0.7              # 70% brightness
    )
    
    # Create and run the effect
    effect = DesktopEffect(controller.client, options)
    
    try:
        print("Starting desktop effect with immediate transitions...")
        print("Colors will change immediately without smooth transitions.")
        print("Press Ctrl+C to stop.")
        
        effect.run()
        
    except KeyboardInterrupt:
        print("\nStopping desktop effect...")
    finally:
        effect.stop()
        controller.turn_off_all_lights()


def main():
    """Main function to run desktop effect examples."""
    print("Desktop Effect Examples")
    print("======================")
    print()
    print("Choose an example to run:")
    print("1. Dominant Color Sampling")
    print("2. Average Color Sampling")
    print("3. Immediate Transitions")
    print("4. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == "1":
                example_dominant_color()
                break
            elif choice == "2":
                example_average_color()
                break
            elif choice == "3":
                example_immediate_transitions()
                break
            elif choice == "4":
                print("Goodbye!")
                break
            else:
                print("Please enter a number between 1 and 4")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main() 