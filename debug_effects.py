#!/usr/bin/env python3
"""
Debug script to test effect discovery
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from classes.EffectDiscovery import EffectDiscovery

def main():
    print("=== Effect Discovery Debug ===")
    
    # Test effect discovery
    print("Discovering effects...")
    effects = EffectDiscovery.discover_effects()
    
    print(f"Found {len(effects)} effects:")
    for effect_name, (effect_class, options_class) in effects.items():
        print(f"  - {effect_name}: {effect_class.__name__} with {options_class.__name__}")
    
    if not effects:
        print("\nNo effects found! Let's debug...")
        
        # Try importing effects module directly
        print("\nTrying to import effects module...")
        try:
            import effects
            print(f"Effects module imported successfully")
            print(f"Effects module dir: {dir(effects)}")
            
            # Check what's in the effects module
            for attr_name in dir(effects):
                attr = getattr(effects, attr_name)
                print(f"  {attr_name}: {type(attr)}")
                
        except ImportError as e:
            print(f"Failed to import effects module: {e}")
        
        # Check if effects files exist
        print("\nChecking effects directory...")
        effects_dir = os.path.join(os.path.dirname(__file__), 'effects')
        if os.path.exists(effects_dir):
            print(f"Effects directory exists: {effects_dir}")
            for filename in os.listdir(effects_dir):
                if filename.endswith('.py'):
                    print(f"  Found: {filename}")
        else:
            print(f"Effects directory not found: {effects_dir}")

if __name__ == "__main__":
    main() 