#!/usr/bin/env python3
"""
Simple debug script to test imports
"""

print("Starting debug...")

try:
    print("1. Testing basic imports...")
    import sys
    import os
    print("✓ Basic imports successful")
    
    print("2. Testing classes import...")
    from classes import Effect, EffectOptions, EffectDiscovery
    print("✓ Classes import successful")
    
    print("3. Testing effects import...")
    import effects
    print("✓ Effects import successful")
    
    print("4. Testing effect discovery...")
    effects_dict = EffectDiscovery.discover_effects()
    print(f"✓ Effect discovery successful, found {len(effects_dict)} effects")
    
    for name, (effect_class, options_class) in effects_dict.items():
        print(f"  - {name}: {effect_class.__name__}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc() 