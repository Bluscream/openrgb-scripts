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

### Lightning
- Simulates lightning strikes with bright flashes and fade-out
- Configurable colors (random or specific)
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

# Lightning effect examples
python __main__.py --effect Lightning --options "color=white,target_mode=random"
python __main__.py --effect Lightning --options "color=random,target_mode=all,fade_min_ms=200,fade_max_ms=800"

# Desktop effect examples
python __main__.py --effect Desktop --options "color_sampling=dominant,capture_interval_ms=100"
python __main__.py --effect Desktop --options "color_sampling=average,smooth_transitions=true,transition_duration_ms=300"

# Audio effect examples
python __main__.py --effect Audio --options "peak_threshold=0.05,peak_duration=0.1"
python __main__.py --effect AudioLoopback --options "use_loopback=true,frequency_bands=[60,250,500,2000,4000,8000]"

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
- `max_brightness`: Brightness multiplier (0.0 to 1.0)

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
from classes import Colors, RAINBOW_COLORS, lerp_color

# Access predefined colors
red_color = Colors.RED.value
blue_color = Colors.BLUE.value

# Use rainbow colors
first_rainbow_color = RAINBOW_COLORS[0]  # Red
all_rainbow_colors = RAINBOW_COLORS      # List of all rainbow colors

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
│   └── audio_loopback.py # Advanced audio loopback effect
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