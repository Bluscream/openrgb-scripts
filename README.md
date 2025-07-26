# OpenRGB Light Flashing Script

This script uses the OpenRGB Python SDK to flash all RGB devices connected to your system in a specific pattern.

## Pattern
The script executes the following light flashing pattern:
- 2x blue flashes (100ms each)
- 500ms pause
- 2x red flashes (100ms each)
- 500ms pause

## Prerequisites

1. **OpenRGB Software**: Make sure you have OpenRGB installed and running
   - Download from: https://openrgb.org/
   - Start OpenRGB with server mode: `openrgb --server`

2. **Python**: Python 3.6 or higher

## Installation

1. Install the required Python package:
   ```bash
   pip install -r requirements.txt
   ```

   Or install directly:
   ```bash
   pip install openrgb-python
   ```

## Usage

1. Make sure OpenRGB is running with server mode enabled
2. Run the script:
   ```bash
   python openrgb_flash_script.py
   ```

## Troubleshooting

- **Connection Error**: If you get a connection refused error, make sure OpenRGB is running with the `--server` flag
- **No Devices Found**: Ensure your RGB devices are properly detected by OpenRGB
- **Permission Issues**: On Linux, you might need to run OpenRGB with sudo or add your user to the appropriate groups

## Features

- Connects to OpenRGB server automatically
- Lists all detected RGB devices
- Flashes all devices with the specified pattern
- Provides detailed console output
- Error handling for common issues

## Customization

You can modify the script to:
- Change colors by modifying the `RGBColor` values
- Adjust timing by changing the `duration_ms` and `time.sleep()` values
- Target specific devices instead of all devices
- Add more complex patterns 