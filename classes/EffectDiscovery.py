"""
Effect discovery and loading utilities.
"""

import importlib
import inspect
from typing import Dict, List, Tuple, Type
from .Effect import Effect
from .EffectOptions import EffectOptions


class EffectDiscovery:
    """
    Utility class for discovering and loading effects dynamically.
    """
    
    @staticmethod
    def discover_effects() -> Dict[str, Tuple[Type[Effect], Type[EffectOptions]]]:
        """
        Discover all available effects in the effects package.
        
        Returns:
            Dictionary mapping effect names to (EffectClass, OptionsClass) tuples
        """
        effects = {}
        
        try:
            # Import the effects package
            effects_module = importlib.import_module('effects')
            
            # Get all attributes from the effects module
            for attr_name in dir(effects_module):
                attr = getattr(effects_module, attr_name)
                
                # Check if it's a class that inherits from Effect
                if (inspect.isclass(attr) and 
                    issubclass(attr, Effect) and 
                    attr != Effect):
                    
                    # Find the corresponding options class
                    options_class = EffectDiscovery._find_options_class(attr_name, effects_module)
                    
                    if options_class:
                        # Use a friendly name (remove "Effect" suffix)
                        effect_name = attr_name.replace('Effect', '')
                        effects[effect_name] = (attr, options_class)
        
        except ImportError as e:
            print(f"Warning: Could not import effects module: {e}")
        
        return effects
    
    @staticmethod
    def _find_options_class(effect_class_name: str, effects_module) -> Type[EffectOptions]:
        """
        Find the corresponding options class for an effect class.
        
        Args:
            effect_class_name: Name of the effect class
            effects_module: The effects module to search in
            
        Returns:
            The options class or None if not found
        """
        # Try to find options class with the same prefix
        options_class_name = effect_class_name.replace('Effect', 'Options')
        
        if hasattr(effects_module, options_class_name):
            options_class = getattr(effects_module, options_class_name)
            if (inspect.isclass(options_class) and 
                issubclass(options_class, EffectOptions)):
                return options_class
        
        # If not found, return the base EffectOptions
        return EffectOptions
    
    @staticmethod
    def get_effect_info(effect_class: Type[Effect], options_class: Type[EffectOptions]) -> Dict:
        """
        Get information about an effect for display purposes.
        
        Args:
            effect_class: The effect class
            options_class: The options class
            
        Returns:
            Dictionary with effect information
        """
        info = {
            'name': effect_class.__name__.replace('Effect', ''),
            'description': effect_class.__doc__ or 'No description available',
            'options': {}
        }
        
        # Get options information
        if options_class != EffectOptions:
            # Get the __init__ method signature
            init_method = getattr(options_class, '__init__', None)
            if init_method:
                sig = inspect.signature(init_method)
                for param_name, param in sig.parameters.items():
                    if param_name != 'self':
                        info['options'][param_name] = {
                            'default': param.default if param.default != inspect.Parameter.empty else None,
                            'annotation': param.annotation if param.annotation != inspect.Parameter.empty else None
                        }
        
        return info 