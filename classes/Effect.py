"""
Base Effect class for OpenRGB effects.
"""

import time
from abc import ABC, abstractmethod
from typing import List, Optional, Union
from openrgb import OpenRGBClient
from openrgb.utils import RGBColor
from .EffectOptions import EffectOptions
from .Colors import Colors, RAINBOW_COLORS


class Effect(ABC):
    """
    Base class for all OpenRGB effects.
    """
    
    def __init__(self, client: OpenRGBClient, options: EffectOptions):
        """
        Initialize the effect.
        
        Args:
            client: OpenRGB client instance
            options: Effect configuration options
        """
        self.client = client
        self.options = options
        self.running = False
    
    def clamp_brightness(self, color: RGBColor) -> RGBColor:
        """
        Clamp the brightness of an RGBColor object based on max_brightness.
        
        Args:
            color: RGBColor object
            
        Returns:
            RGBColor object with clamped brightness
        """
        r = int(color.red * self.options.max_brightness)
        g = int(color.green * self.options.max_brightness)
        b = int(color.blue * self.options.max_brightness)
        return RGBColor(r, g, b)
    
    def get_target_devices(self) -> List:
        """
        Get the list of devices to target based on devices list.
        
        Returns:
            List of device objects to target
        """
        # If devices is None or empty, use all devices
        if not self.options.devices:
            return self.client.devices
        
        # If devices list is provided, use those specific devices
        return [self.client.devices[i] for i in self.options.devices 
               if i < len(self.client.devices)]
    
    def set_devices_color(self, devices: List, color: RGBColor):
        """
        Set specific devices to a color.
        
        Args:
            devices: List of device objects
            color: RGBColor object
        """
        clamped_color = self.clamp_brightness(color)
        for device in devices:
            if hasattr(device, 'set_color'):
                device.set_color(clamped_color)
    
    def set_all_target_devices_color(self, color: RGBColor):
        """
        Set all target devices to a color.
        
        Args:
            color: RGBColor object
        """
        devices = self.get_target_devices()
        self.set_devices_color(devices, color)
    
    def turn_off_target_devices(self):
        """
        Turn off all target devices (set to black).
        """
        self.set_all_target_devices_color(Colors.BLACK.value)
    
    @abstractmethod
    def start(self):
        """
        Initialize the effect. Called once before the loop starts.
        """
        pass
    
    @abstractmethod
    def loop(self):
        """
        Execute one iteration of the effect loop.
        """
        pass
    
    @abstractmethod
    def stop(self):
        """
        Clean up the effect. Called when the effect is stopped.
        """
        pass
    
    def run(self):
        """
        Run the effect in a continuous loop until stopped.
        """
        self.running = True
        self.start()
        
        try:
            while self.running:
                self.loop()
                time.sleep(self.options.sleep_s)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()
    
    def stop_effect(self):
        """
        Stop the effect loop.
        """
        self.running = False 