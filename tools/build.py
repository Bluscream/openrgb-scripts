#!/usr/bin/env python3
"""
Build script for creating executable from OpenRGB Effects Controller
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_pyinstaller():
    """Install PyInstaller if not already installed."""
    try:
        import PyInstaller
        print("PyInstaller is already installed.")
    except ImportError:
        print("Installing PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "ensurepip", "--upgrade"])
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller","imp"])
            print("PyInstaller installed successfully.")
            import PyInstaller
        except subprocess.CalledProcessError as ex:
            print(f"Failed to install PyInstaller via pip. Error: {ex}")

def build_executable():
    """Build the executable using PyInstaller."""
    
    # Get the project root directory
    project_root = Path(__file__).parent.parent

    main_file = project_root / "__main__.py"

    print(f"Project root: {project_root}")
    print(f"Main file: {main_file}")
    print(f"Main file exists: {main_file.exists()}")
    
    # PyInstaller command using Python module approach
    cmd = [
        sys.executable, "-m", "PyInstaller.__main__",
        "--onefile",  # Create a single executable file
        "--name=openrgb_effects",  # Name of the executable
        "--distpath=dist",  # Output directory
        "--workpath=build",  # Build directory
        "--specpath=build",  # Spec file directory
        "--clean",  # Clean cache before building
        "--noconfirm",  # Replace existing files without asking
        # Add data files if needed
        "--add-data=classes;classes",  # Include classes directory
        "--add-data=effects;effects",  # Include effects directory
        # Hidden imports for dependencies
        "--hidden-import=openrgb",
        "--hidden-import=PIL",
        "--hidden-import=sounddevice",
        "--hidden-import=numpy",
        "--hidden-import=argparse",
        # Icon (optional - you can add an icon file later)
        # "--icon=icon.ico",
        str(main_file)
    ]
    
    print("Building executable...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd, cwd=project_root)
        print("\n✅ Build completed successfully!")
        print(f"Executable location: {project_root / 'dist' / 'openrgb_effects.exe'}")
        
        # Copy the executable to the tools directory for convenience
        exe_source = project_root / "dist" / "openrgb_effects.exe"
        exe_dest = project_root / "tools" / "openrgb_effects.exe"
        
        if exe_source.exists():
            shutil.copy2(exe_source, exe_dest)
            print(f"Copied executable to: {exe_dest}")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed with error: {e}")
        return False
    
    return True

def create_batch_files():
    """Create batch files for easy execution of effects."""
    project_root = Path(__file__).parent
    tools_dir = project_root / "tools"
    
    # Create batch files for common effects
    effects = [
        ("rainbow", "Rainbow", "sleep_s=1,max_brightness=.3"),
        ("breathing", "Breathing", "sleep_s=1,max_brightness=.5"),
        ("static", "Static", "sleep_s=1,max_brightness=.5"),
        ("lightning", "Lightning", "sleep_s=0.1,max_brightness=.8"),
        ("police", "PoliceLights", "sleep_s=0.5,max_brightness=.7"),
        ("audio", "Audio", "sleep_s=0.05,max_brightness=.6"),
        ("desktop", "Desktop", "sleep_s=0.1,max_brightness=.4"),
        ("random", "RandomColors", "sleep_s=1,max_brightness=.5")
    ]
    
    for effect_name, effect_class, options in effects:
        batch_file = tools_dir / f"{effect_name}_exe.cmd"
        content = f"""@echo off
echo Starting {effect_name} effect...
"%~dp0openrgb_effects.exe" --effect {effect_class} -o "{options}"
pause
"""
        
        with open(batch_file, 'w') as f:
            f.write(content)
        
        print(f"Created: {batch_file}")

def main():
    """Main build process."""
    print("🚀 OpenRGB Effects Controller - Executable Builder")
    print("=" * 50)
    
    # Install PyInstaller
    install_pyinstaller()
    
    # Build the executable
    if build_executable():
        # Create batch files for easy execution
        create_batch_files()
        
        print("\n🎉 Build process completed!")
        print("\nUsage:")
        print("1. Run the executable directly:")
        print("   dist/openrgb_effects.exe --effect Rainbow")
        print("\n2. Use the batch files in the tools directory:")
        print("   tools/rainbow_exe.cmd")
        print("   tools/breathing_exe.cmd")
        print("   etc.")
        print("\n3. Interactive mode:")
        print("   dist/openrgb_effects.exe")
    else:
        print("\n❌ Build process failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 