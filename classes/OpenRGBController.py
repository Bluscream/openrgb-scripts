"""
OpenRGB Controller class for managing effects.
"""

import sys
import time
from openrgb import OpenRGBClient
from openrgb.utils import RGBColor
from .EffectDiscovery import EffectDiscovery


class OpenRGBController:
    """
    Main controller for OpenRGB effects.
    """
    
    def __init__(self):
        """Initialize the controller."""
        self.client = None
        self.current_effect = None
    
    def connect(self):
        """Connect to the OpenRGB server."""
        try:
            print("Connecting to OpenRGB server...")
            self.client = OpenRGBClient()
            print(f"Connected! Found {len(self.client.devices)} devices:")
            for i, device in enumerate(self.client.devices):
                print(f"  {i+1}. {device.name} ({device.type})")
            return True
        except Exception as e:
            print(f"Error connecting to OpenRGB server: {e}")
            print("Make sure OpenRGB is running with: openrgb --server")
            return False
    
    def run_effect(self, effect_name: str, **options):
        """Run a specific effect by name."""
        effects = EffectDiscovery.discover_effects()
        
        if effect_name not in effects:
            available_effects = list(effects.keys())
            raise ValueError(f"Effect '{effect_name}' not found. Available effects: {available_effects}")
        
        effect_class, options_class = effects[effect_name]
        
        # Create options instance
        opts = options_class(**options)
        
        # Create and run effect
        effect = effect_class(self.client, opts)
        self._run_effect(effect, effect_name)
    
    def get_available_effects(self):
        """Get list of available effects."""
        return list(EffectDiscovery.discover_effects().keys())
    
    def get_effect_info(self, effect_name: str):
        """Get information about a specific effect."""
        effects = EffectDiscovery.discover_effects()
        
        if effect_name not in effects:
            return None
        
        effect_class, options_class = effects[effect_name]
        return EffectDiscovery.get_effect_info(effect_class, options_class)
    
    def _run_effect(self, effect, effect_name):
        """Run an effect with proper error handling."""
        try:
            print(f"\nStarting {effect_name} effect...")
            print("Press Ctrl+C to stop")
            effect.run()
        except KeyboardInterrupt:
            print(f"\nStopping {effect_name} effect...")
        finally:
            if effect:
                effect.stop()
    
    def turn_off_all_lights(self):
        """Turn off all RGB devices."""
        if self.client:
            black = RGBColor(0, 0, 0)
            for device in self.client.devices:
                if hasattr(device, 'set_color'):
                    device.set_color(black)
            print("All lights turned off.") 