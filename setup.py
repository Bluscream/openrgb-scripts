#!/usr/bin/env python3
"""
Setup script for cx_Freeze to create executable
"""

import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": [
        "openrgb", 
        "PIL", 
        "sounddevice", 
        "numpy", 
        "argparse",
        "classes",
        "effects"
    ],
    "excludes": [],
    "include_files": [
        ("classes", "classes"),
        ("effects", "effects"),
    ],
    "include_msvcr": True,
}

# GUI applications require a different base on Windows
base = None
if sys.platform == "win32":
    base = "Console"

setup(
    name="OpenRGB Effects Controller",
    version="1.0",
    description="OpenRGB Effects Controller - Modular lighting effects system",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "__main__.py", 
            base=base,
            target_name="openrgb_effects.exe"
        )
    ]
) 