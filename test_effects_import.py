#!/usr/bin/env python3
"""
Test effects import specifically
"""

import sys
import os
import traceback

print("Testing effects import...")

try:
    # Test importing effects module
    print("Importing effects module...")
    import effects
    print("✓ Effects module imported successfully")
    
    # Check what's in the effects module
    print(f"Effects module contents: {dir(effects)}")
    
    # Try to find effect classes
    effect_classes = []
    for attr_name in dir(effects):
        attr = getattr(effects, attr_name)
        print(f"  {attr_name}: {type(attr)}")
        if hasattr(attr, '__name__') and 'Effect' in attr.__name__:
            effect_classes.append(attr_name)
    
    print(f"Found effect classes: {effect_classes}")
    
except Exception as e:
    print(f"✗ Error importing effects: {e}")
    traceback.print_exc() 