# OpenRGB Effects Controller

A modular system for controlling OpenRGB devices with various lighting effects.

## Features

- **Dynamic Effect Discovery**: Effects are automatically discovered at runtime - no hardcoding required
- **Modular Effect System**: Each effect is a separate class implementing a common interface
- **Configurable Options**: Each effect has its own options class for fine-tuning
- **Device Selection**: Target all devices, random devices, or specific devices
- **Brightness Control**: Global brightness control for all effects
- **Extensible**: Easy to add new effects by implementing the base Effect class
- **Command Line Interface**: Run effects directly with custom options
- **Interactive Mode**: User-friendly menu system for effect selection and configuration

## Effects

### Police Lights
- Alternating blue and red flashes
- Configurable flash duration and pause times

### Rainbow
- Smooth or discrete color transitions
- Configurable transition speed and smoothness

### Random Colors
- Random color assignment per device or all devices
- Customizable color palette

### Static
- Sets devices to a specific color and keeps them static
- Supports any color (named colors, RGB values, hex codes, or 'random')
- Configurable brightness control
- Perfect for setting a solid color across all devices

### Lightning
- Simulates lightning strikes with bright flashes and fade-out
- Configurable colors (random, named colors, RGB values, or hex codes)
- Targets random devices or all devices
- Adjustable fade-out timing (100-500ms)

### Desktop
- Captures screenshots of the main display
- Sets device colors based on dominant or average screen color
- Configurable capture interval and color sampling method
- Smooth color transitions with adjustable duration
- Color tolerance settings for dominant color detection

### Audio
- Listens to audio input and flashes devices in random colors when peaks are detected
- Configurable peak threshold, duration, and fade timing
- Real-time audio processing with PyAudio

### Audio Loopback
- Advanced audio effect that listens to system audio output using loopback recording
- Frequency-based color mapping (bass = red, treble = purple, etc.)
- Configurable frequency bands and audio analysis
- Supports both loopback recording and microphone input
- Real-time FFT analysis for frequency detection

### Breathing
- Smoothly fades a color in and out to create a breathing effect
- Configurable breathing speed (cycles per second)
- Adjustable minimum brightness for subtle breathing
- Supports any color (named colors, RGB values, hex codes, or 'random')

## Installation

1. Install the required Python package:
   ```bash
   pip install -r requirements.txt
   ```

2. Make sure OpenRGB is running with server mode:
   ```bash
   openrgb --server
   ```

## Usage

### Interactive Mode (Default)
Run the interactive mode to discover and select effects dynamically:
```bash
python __main__.py
```

### Command Line Mode
Run specific effects with custom options:

```bash
# List all available effects
python __main__.py --list

# Run a specific effect with default options
python __main__.py --effect Rainbow

# Run with custom options
python __main__.py --effect PoliceLights --options "max_brightness=0.5,flash_duration_ms=200"

# Run with multiple options
python __main__.py --effect RandomColors --options "per_device=true,sleep_s=0.3"

# Static effect examples
python __main__.py --effect Static --options "color=blue,max_brightness=0.8"
python __main__.py --effect Static --options "color=255,0,255,max_brightness=50%"
python __main__.py --effect Static --options "color=#00FF00,max_brightness=random"
python __main__.py --effect Static --options "color=random,max_brightness=0.7"

# Lightning effect examples
python __main__.py --effect Lightning --options "color=white,target_mode=random"
python __main__.py --effect Lightning --options "color=random,target_mode=all,fade_min_ms=200,fade_max_ms=800"
python __main__.py --effect Lightning --options "color=255,0,255,target_mode=all,flash_duration_ms=100"

# Desktop effect examples
python __main__.py --effect Desktop --options "color_sampling=dominant,capture_interval_ms=100"
python __main__.py --effect Desktop --options "color_sampling=average,smooth_transitions=true,transition_duration_ms=300"

# Audio effect examples
python __main__.py --effect Audio --options "peak_threshold=0.05,peak_duration=0.1"
python __main__.py --effect AudioLoopback --options "use_loopback=true,frequency_bands=[60,250,500,2000,4000,8000]"

# Breathing effect examples
python __main__.py --effect Breathing --options "color=red,breathing_speed=1.5"
python __main__.py --effect Breathing --options "color=255,0,255,breathing_speed=3,min_brightness=20%"
python __main__.py --effect Breathing --options "color=#00FF00,breathing_speed=0.8,min_brightness=random"
python __main__.py --effect Breathing --options "color=random,breathing_speed=2.0,min_brightness=0.1"

### Windows Command Files

For Windows users, convenient command files are available in the `tools/` directory:

```cmd
# Basic breathing effect (white, speed 2, min brightness 0.1)
tools\breathing.cmd

# Custom breathing parameters (color, speed, min_brightness, max_brightness)
tools\breathing.cmd red 1.5 0.2 0.8

# Static color effect
tools\static.cmd blue 0.7

# Rainbow effect
tools\rainbow.cmd
```

### Programmatic Usage

```python
from openrgb import OpenRGBClient
from classes import OpenRGBController

# Create controller
controller = OpenRGBController()
controller.connect()

# Run a specific effect
controller.run_effect("PoliceLights", max_brightness=0.7, flash_duration_ms=150)

# Run on specific devices
controller.run_effect("Rainbow", devices=[0, 2], max_brightness=0.5)

# Get available effects
effects = controller.get_available_effects()
print(f"Available effects: {effects}")

# Get effect information
info = controller.get_effect_info("Rainbow")
print(f"Rainbow effect options: {info['options']}")
```

### Effect Options

All effects support these common options:
- `sleep_s`: Sleep time between iterations
- `devices`: List of device indices to target (None or empty for all devices)
- `max_brightness`: Brightness multiplier (0.0 to 1.0, or "50%", "random")

### Device Selection

```python
# Target all devices (default)
options = EffectOptions()  # or devices=None

# Target specific devices
options = EffectOptions(devices=[0, 2])  # Devices 0 and 2

# Target a single device
options = EffectOptions(devices=[1])  # Device 1 only
```

### Using Colors

```python
from classes import Colors, RAINBOW_COLORS, lerp_color, parse_color, parse_brightness

# Access predefined colors
red_color = Colors.RED.value
blue_color = Colors.BLUE.value

# Use rainbow colors
first_rainbow_color = RAINBOW_COLORS[0]  # Red
all_rainbow_colors = RAINBOW_COLORS      # List of all rainbow colors

# Parse colors from strings
red = parse_color('red')
purple = parse_color('255,0,255')
green = parse_color('#00FF00')
random_color = parse_color('random')

# Parse brightness from strings
half_brightness = parse_brightness('0.5')
quarter_brightness = parse_brightness('25%')
random_brightness = parse_brightness('random')

# Interpolate between colors
mid_color = lerp_color(Colors.RED.value, Colors.BLUE.value, 0.5)  # Purple
```

## Creating Custom Effects

To create a new effect, inherit from the `Effect` base class:

```python
from classes import Effect, EffectOptions

class MyEffectOptions(EffectOptions):
    def __init__(self, custom_param=10, **kwargs):
        super().__init__(**kwargs)
        self.custom_param = custom_param

class MyEffect(Effect):
    def __init__(self, client, options: MyEffectOptions):
        super().__init__(client, options)
    
    def start(self):
        """Initialize the effect."""
        print("Starting my effect...")
    
    def loop(self):
        """Execute one iteration of the effect."""
        # Your effect logic here
        pass
    
    def stop(self):
        """Clean up the effect."""
        print("Stopping my effect...")
        self.turn_off_target_devices()
```

## Project Structure

```
openrgb/
├── __main__.py          # Main script with dynamic effect discovery
├── classes/             # Classes package
│   ├── __init__.py      # Package exports
│   ├── OpenRGBController.py # Main controller class
│   ├── EffectOptions.py # Effect configuration options
│   ├── Effect.py        # Base Effect class
│   ├── Colors.py        # Color definitions and rainbow sequence
│   └── EffectDiscovery.py # Dynamic effect discovery utilities
├── effects/             # Effects package
│   ├── __init__.py      # Package exports
│   ├── police_lights.py # Police lights effect
│   ├── rainbow.py       # Rainbow effect
│   ├── random_colors.py # Random colors effect
│   ├── lightning.py     # Lightning effect
│   ├── desktop.py       # Desktop color sampling effect
│   ├── audio.py         # Audio input effect
│   ├── audio_loopback.py # Advanced audio loopback effect
│   └── breathing.py     # Breathing effect
├── tools/               # Windows command files
│   ├── breathing.cmd    # Breathing effect command
│   ├── static.cmd       # Static color command
│   ├── rainbow.cmd      # Rainbow effect command
│   └── lighting.cmd     # Lighting effect command
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Troubleshooting

- **Connection Error**: Make sure OpenRGB is running with `--server` flag
- **No Devices Found**: Ensure your RGB devices are properly detected by OpenRGB
- **Permission Issues**: On Linux, you might need to run OpenRGB with sudo
- **Audio Effects Not Working**: 
  - For loopback recording, enable "Stereo Mix" in Windows sound settings
  - Install virtual audio cable software for better loopback support
  - Try setting `use_loopback=False` to use microphone input instead
  - Adjust `peak_threshold` if the effect is too sensitive or not sensitive enough

## Contributing

To add a new effect:
1. Create a new file in the `effects/` directory
2. Implement the `Effect` base class
3. Create a corresponding `Options` class
4. Add the effect to `effects/__init__.py`
5. Update the demo in `__main__.py` if desired 