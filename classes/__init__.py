"""
Classes package for OpenRGB effects controller.
"""

from openrgb.utils import RGBColor
from .OpenRGBController import OpenRGBController
from .EffectOptions import EffectOptions
from .Effect import Effect
from .Colors import Colors, RAINBOW_COLORS, lerp_color
from .EffectDiscovery import EffectDiscovery

__all__ = ['OpenRGBController', 'EffectOptions', 'Effect', 'Colors', 'RAINBOW_COLORS', 'lerp_color', 'EffectDiscovery', 'RGBColor'] 