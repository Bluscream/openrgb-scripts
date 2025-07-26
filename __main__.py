#!/usr/bin/env python3
"""
OpenRGB Effects Controller

This script provides a modular system for controlling OpenRGB devices
with various lighting effects. Effects are discovered dynamically at runtime.
"""

import sys
import argparse
from classes import OpenRGBController
from classes.EffectDiscovery import EffectDiscovery
from classes.HASS import HASSLightController


def display_effects_menu(controller):
    """Display available effects and get user selection."""
    effects = controller.get_available_effects()
    
    if not effects:
        print("No effects found!")
        return None
    
    print("\n=== Available Effects ===")
    for i, effect_name in enumerate(effects, 1):
        info = controller.get_effect_info(effect_name)
        description = info['description'].split('\n')[0] if info['description'] else 'No description'
        print(f"{i}. {effect_name} - {description}")
    
    print(f"{len(effects) + 1}. Exit")
    
    while True:
        try:
            choice = input(f"\nSelect an effect (1-{len(effects) + 1}): ").strip()
            choice_num = int(choice)
            
            if 1 <= choice_num <= len(effects):
                return effects[choice_num - 1]
            elif choice_num == len(effects) + 1:
                return None
            else:
                print(f"Please enter a number between 1 and {len(effects) + 1}")
        except ValueError:
            print("Please enter a valid number")
        except KeyboardInterrupt:
            return None


def get_effect_options(controller, effect_name):
    """Get effect options from user or use defaults."""
    from classes import parse_brightness
    
    info = controller.get_effect_info(effect_name)
    
    # Call effect's info() method
    effects = EffectDiscovery.discover_effects()
    if effect_name in effects:
        effect_class, _ = effects[effect_name]
        effect_class.info()
    
    if not info['options']:
        print(f"Using default options for {effect_name}")
        return {}
    
    print(f"\n=== {effect_name} Options ===")
    print("Press Enter to use default values, or enter custom values:")
    print("For brightness values, you can use: 0.5, 50%, random")
    
    options = {}
    for param_name, param_info in info['options'].items():
        default = param_info['default']
        param_type = param_info['annotation']
        
        # Skip self parameter
        if param_name == 'self':
            continue
        
        # Display parameter info
        if default is not None:
            prompt = f"{param_name} (default: {default}): "
        else:
            # Check if the parameter type allows None
            if param_type and hasattr(param_type, '__origin__') and param_type.__origin__ is list:
                if param_name == 'devices':
                    prompt = f"{param_name} (default: None, empty for all devices): "
                elif param_name == 'color_palette':
                    prompt = f"{param_name} (default: None, empty for all colors): "
                else:
                    prompt = f"{param_name} (default: None, enter 'none' for default colors): "
            else:
                prompt = f"{param_name}: "
        
        while True:
            try:
                value = input(prompt).strip()
                
                if not value and default is not None:
                    # Use default value
                    options[param_name] = default
                    break
                elif not value and default is None:
                    # For devices and color_palette parameters, empty means use all (None)
                    if param_name in ['devices', 'color_palette']:
                        options[param_name] = None
                        break
                    else:
                        print("This parameter requires a value")
                        continue
                else:
                    # Handle brightness-related parameters with parse_brightness
                    if param_name in ['max_brightness', 'min_brightness', 'brightness']:
                        try:
                            options[param_name] = parse_brightness(value)
                            break
                        except Exception as e:
                            print(f"Invalid brightness value: {e}")
                            continue
                    # Parse the value
                    elif value.lower() == 'none':
                        options[param_name] = None
                    elif param_type == bool:
                        if value.lower() in ('true', '1', 'yes', 'on'):
                            options[param_name] = True
                        elif value.lower() in ('false', '0', 'no', 'off'):
                            options[param_name] = False
                        else:
                            print("Please enter 'true' or 'false'")
                            continue
                    elif param_type == int:
                        options[param_name] = int(value)
                    elif param_type == float:
                        options[param_name] = float(value)
                    else:
                        # String or unknown type
                        options[param_name] = value
                    break
            except ValueError:
                print(f"Invalid value for {param_name}")
            except KeyboardInterrupt:
                return None
    
    return options


def run_interactive_mode(controller):
    """Run the interactive mode."""
    print("=== OpenRGB Effects Controller ===")
    print("Dynamic effect discovery enabled!")
    
    while True:
        # Display effects menu
        effect_name = display_effects_menu(controller)
        
        if effect_name is None:
            print("Goodbye!")
            break
        
        # Get effect options
        options = get_effect_options(controller, effect_name)
        
        if options is None:
            print("Cancelled by user")
            continue
        
        # Run the effect
        try:
            print(f"\nStarting {effect_name} effect...")
            controller.run_effect(effect_name, **options)
        except KeyboardInterrupt:
            print(f"\nStopped {effect_name} effect")
        except Exception as e:
            print(f"Error running {effect_name}: {e}")
            print("Tip: Check that all option values are correct and try again.")


def run_direct_mode(controller, effect_name, options, exit_after_one=False):
    """Run a specific effect directly."""
    try:
        print(f"Starting {effect_name} effect...")
        if exit_after_one:
            print("Exit mode: Will skip cleanup and exit after one iteration")
        controller.run_effect(effect_name, **options, exit_after_one=exit_after_one)
    except KeyboardInterrupt:
        print(f"\nStopped {effect_name} effect")
    except Exception as e:
        print(f"Error running {effect_name}: {e}")
        sys.exit(1)


def list_effects(controller):
    """List all available effects."""
    effects = controller.get_available_effects()
    
    if not effects:
        print("No effects found!")
        return
    
    print("Available effects:")
    for effect_name in effects:
        info = controller.get_effect_info(effect_name)
        description = info['description'].split('\n')[0] if info['description'] else 'No description'
        print(f"  {effect_name}: {description}")
        
        # Show options if any
        if info['options']:
            print("    Options:")
            for param_name, param_info in info['options'].items():
                if param_name != 'self':
                    default = param_info['default']
                    param_type = param_info['annotation']
                    type_name = getattr(param_type, '__name__', str(param_type))
                    if default is not None:
                        print(f"      {param_name} ({type_name}): {default}")
                    else:
                        print(f"      {param_name} ({type_name})")


def parse_options(options_str):
    """Parse options string into dictionary."""
    if not options_str:
        return {}
    
    from classes import parse_brightness
    
    options = {}
    for option in options_str.split(','):
        if '=' in option:
            key, value = option.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            # Handle brightness-related parameters with parse_brightness
            if key in ['max_brightness', 'min_brightness', 'brightness']:
                try:
                    options[key] = parse_brightness(value)
                except Exception:
                    # Fallback to original parsing if parse_brightness fails
                    try:
                        if value.lower() == 'none':
                            options[key] = None
                        elif '.' in value:
                            options[key] = float(value)
                        else:
                            options[key] = int(value)
                    except ValueError:
                        options[key] = value
            else:
                # Try to parse as different types
                try:
                    if value.lower() == 'none':
                        options[key] = None
                    elif value.lower() in ('true', 'false'):
                        options[key] = value.lower() == 'true'
                    elif '.' in value:
                        options[key] = float(value)
                    else:
                        options[key] = int(value)
                except ValueError:
                    # Keep as string
                    options[key] = value
    
    return options


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="OpenRGB Effects Controller - Dynamic effect discovery and control",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Interactive mode
  %(prog)s --list             # List available effects
  %(prog)s --effect Rainbow   # Run Rainbow effect with defaults
  %(prog)s --effect PoliceLights --options "max_brightness=0.5,flash_duration_ms=200"
  %(prog)s --effect RandomColors --options "per_device=true,sleep_s=0.3"
  %(prog)s --effect Rainbow --options "devices=[0,2],max_brightness=0.5"
        """
    )
    
    parser.add_argument(
        '--effect', '-e',
        help='Effect to run (use --list to see available effects)'
    )
    
    parser.add_argument(
        '--options', '-o',
        help='Comma-separated options (e.g., "max_brightness=0.5,sleep_s=0.1")'
    )
    
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='List all available effects'
    )
    
    parser.add_argument(
        '--exit',
        action='store_true',
        help='Skip cleanup and exit after one iteration (for static effects)'
    )
    
    args = parser.parse_args()
    
    # Initialize controller
    controller = OpenRGBController()
    
    if not controller.connect():
        print("Failed to connect to OpenRGB server. Make sure OpenRGB is running with --server flag.")
        sys.exit(1)
    
    try:
        hass = HASSLightController()
        hass.set_effect("DDP", [
            "light.esphome_blu_pc_kvm_desk_rgb_led_strip",
            "light.esphome_closet_rgb_led_strip_2",
            "light.esphome_suitcase_rgb_led_strip",
            "light.esphome_closet_virtual_e1_31_light"
        ])
    except Exception as e:
        print(f"Error setting effect on Home Assistant lights: {e}")

    try:
        if args.list:
            # List effects mode
            list_effects(controller)
        elif args.effect:
            # Direct mode
            options = parse_options(args.options)
            run_direct_mode(controller, args.effect, options, args.exit)
        else:
            # Interactive mode
            run_interactive_mode(controller)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        if not args.exit:
            controller.turn_off_all_lights()


if __name__ == "__main__":
    main() 