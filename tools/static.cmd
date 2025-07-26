@echo off
cd /d "%~dp0\.."
set "color=%1"
if "%color%"=="" set "color=white"
set "brightness=%2"
if "%brightness%"=="" set "brightness=1"
python __main__.py --effect Static -o "color=%color%,max_brightness=%brightness%" --exit 