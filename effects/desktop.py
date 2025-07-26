"""
Desktop effect - captures screenshots and sets device colors based on dominant screen color.
"""

import time
from PIL import ImageGrab, Image
from collections import Counter
from classes import Effect, EffectOptions, Colors, RGBColor


class DesktopOptions(EffectOptions):
    """
    Options for desktop effect.
    """
    
    def __init__(self, 
                 sleep_s: float = 0.1,
                 devices: list = None,
                 max_brightness: float = 1.0,
                 capture_interval_ms: int = 100,
                 color_sampling: str = "dominant",
                 color_tolerance: int = 30,
                 smooth_transitions: bool = True,
                 transition_duration_ms: int = 200):
        """
        Initialize desktop options.
        
        Args:
            capture_interval_ms: How often to capture screenshots in milliseconds
            color_sampling: "dominant" (most common color) or "average" (average color)
            color_tolerance: Tolerance for grouping similar colors (0-255)
            smooth_transitions: Whether to smoothly transition between colors
            transition_duration_ms: Duration of color transitions in milliseconds
        """
        super().__init__(sleep_s, devices, max_brightness)
        self.capture_interval_ms = capture_interval_ms
        self.color_sampling = color_sampling
        self.color_tolerance = color_tolerance
        self.smooth_transitions = smooth_transitions
        self.transition_duration_ms = transition_duration_ms


class DesktopEffect(Effect):
    """
    Desktop effect - captures screenshots and sets device colors based on dominant screen color.
    
    This effect:
    1. Captures a screenshot of the main display
    2. Analyzes the colors to find the dominant or average color
    3. Sets all target devices to that color
    4. Repeats at the specified interval
    """
    
    def __init__(self, client, options: DesktopOptions):
        super().__init__(client, options)
        self.current_color = Colors.BLACK.value
        self.target_color = Colors.BLACK.value
        self.transition_start_time = None
        
    def start(self):
        """Initialize the effect."""
        print("Starting desktop effect...")
        print(f"Capture interval: {self.options.capture_interval_ms}ms")
        print(f"Color sampling: {self.options.color_sampling}")
        print(f"Color tolerance: {self.options.color_tolerance}")
        print(f"Smooth transitions: {self.options.smooth_transitions}")
        
    def capture_screenshot(self):
        """
        Capture a screenshot of the main display.
        
        Returns:
            PIL Image object of the screenshot
        """
        try:
            # Capture the entire screen
            screenshot = ImageGrab.grab()
            return screenshot
        except Exception as e:
            print(f"Error capturing screenshot: {e}")
            return None
    
    def analyze_colors(self, image):
        """
        Analyze the colors in the image to find dominant or average color.
        
        Args:
            image: PIL Image object
            
        Returns:
            RGBColor object representing the analyzed color
        """
        if image is None:
            return Colors.BLACK.value
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Get all pixels as a list of RGB tuples
        pixels = list(image.getdata())
        
        if self.options.color_sampling == "dominant":
            return self._get_dominant_color(pixels)
        else:  # average
            return self._get_average_color(pixels)
    
    def _get_dominant_color(self, pixels):
        """
        Find the most dominant color in the image.
        
        Args:
            pixels: List of RGB tuples
            
        Returns:
            RGBColor object
        """
        # Group similar colors using tolerance
        tolerance = self.options.color_tolerance
        
        # Quantize colors to reduce similar colors
        quantized_pixels = []
        for r, g, b in pixels:
            # Quantize to tolerance level
            r_quantized = (r // tolerance) * tolerance
            g_quantized = (g // tolerance) * tolerance
            b_quantized = (b // tolerance) * tolerance
            quantized_pixels.append((r_quantized, g_quantized, b_quantized))
        
        # Count occurrences of each color
        color_counts = Counter(quantized_pixels)
        
        # Get the most common color
        if color_counts:
            dominant_rgb = max(color_counts, key=color_counts.get)
            return RGBColor(dominant_rgb[0], dominant_rgb[1], dominant_rgb[2])
        
        return Colors.BLACK.value
    
    def _get_average_color(self, pixels):
        """
        Calculate the average color of the image.
        
        Args:
            pixels: List of RGB tuples
            
        Returns:
            RGBColor object
        """
        if not pixels:
            return Colors.BLACK.value
        
        # Calculate average RGB values
        total_r = sum(pixel[0] for pixel in pixels)
        total_g = sum(pixel[1] for pixel in pixels)
        total_b = sum(pixel[2] for pixel in pixels)
        
        num_pixels = len(pixels)
        avg_r = int(total_r / num_pixels)
        avg_g = int(total_g / num_pixels)
        avg_b = int(total_b / num_pixels)
        
        return RGBColor(avg_r, avg_g, avg_b)
    
    def lerp_color(self, color1: RGBColor, color2: RGBColor, t: float) -> RGBColor:
        """
        Linear interpolation between two colors.
        
        Args:
            color1: Starting color
            color2: Ending color
            t: Interpolation factor (0.0 to 1.0)
            
        Returns:
            Interpolated RGBColor
        """
        r = int(color1.red + (color2.red - color1.red) * t)
        g = int(color1.green + (color2.green - color1.green) * t)
        b = int(color1.blue + (color2.blue - color1.blue) * t)
        return RGBColor(r, g, b)
    
    def loop(self):
        """Execute one iteration of the desktop effect."""
        # Capture screenshot
        screenshot = self.capture_screenshot()
        
        # Analyze colors
        new_target_color = self.analyze_colors(screenshot)
        
        # Update target color if it's significantly different
        if (abs(new_target_color.red - self.target_color.red) > 10 or
            abs(new_target_color.green - self.target_color.green) > 10 or
            abs(new_target_color.blue - self.target_color.blue) > 10):
            
            self.target_color = new_target_color
            
            if self.options.smooth_transitions:
                # Start smooth transition
                self.transition_start_time = time.time()
            else:
                # Immediate color change
                self.current_color = self.target_color
                self.set_all_target_devices_color(self.current_color)
        
        # Handle smooth transitions
        if (self.options.smooth_transitions and 
            self.transition_start_time is not None and
            self.current_color != self.target_color):
            
            elapsed = time.time() - self.transition_start_time
            duration = self.options.transition_duration_ms / 1000.0
            progress = min(elapsed / duration, 1.0)
            
            # Interpolate between current and target color
            interpolated_color = self.lerp_color(self.current_color, self.target_color, progress)
            self.set_all_target_devices_color(interpolated_color)
            
            # Update current color
            self.current_color = interpolated_color
            
            # Check if transition is complete
            if progress >= 1.0:
                self.transition_start_time = None
        elif not self.options.smooth_transitions:
            # For immediate transitions, just set the color
            self.set_all_target_devices_color(self.current_color)
    
    def stop(self):
        """Clean up the effect."""
        print("Stopping desktop effect...")
        self.turn_off_target_devices() 