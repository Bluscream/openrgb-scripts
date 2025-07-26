"""
OpenRGB Effects Package

This package contains various lighting effects for OpenRGB devices.
"""

import os
import importlib
import inspect
from classes import Effect, Colors, RAINBOW_COLORS

# Automatically discover and import all effect classes
def _discover_effects():
    """Dynamically discover all effect classes in this package."""
    effects = {}
    current_dir = os.path.dirname(__file__)
    
    # Get all .py files in the current directory
    for filename in os.listdir(current_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            module_name = filename[:-3]  # Remove .py extension
            
            try:
                # Import the module
                module = importlib.import_module(f'.{module_name}', package=__name__)
                
                # Find Effect and Options classes in the module
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    
                    # Check if it's a class and inherits from Effect
                    if (inspect.isclass(attr) and 
                        issubclass(attr, Effect) and 
                        attr != Effect):
                        effects[attr_name] = attr
                    
                    # Also collect Options classes (those ending with 'Options')
                    elif (inspect.isclass(attr) and 
                          attr_name.endswith('Options')):
                        effects[attr_name] = attr
                        
            except ImportError as e:
                print(f"Warning: Could not import {module_name}: {e}")
            except Exception as e:
                print(f"Warning: Error processing {module_name}: {e}")
    
    return effects

# Import all discovered effects
_discovered_effects = _discover_effects()

# Add all discovered effects to the module's namespace
globals().update(_discovered_effects)

# Create __all__ list with all discovered effects plus the base classes
__all__ = ['Effect', 'Colors', 'RAINBOW_COLORS'] + list(_discovered_effects.keys())
