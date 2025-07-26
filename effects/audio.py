"""
Audio effects - listen to audio and flash devices based on audio peaks.
"""

import time
import random
import threading
import math
import sounddevice as sd
from classes import Effect, EffectOptions, Colors, RGBColor


class AudioOptions(EffectOptions):
    def __init__(self, sample_rate=44100, chunk_size=1024, peak_threshold=0.05, 
                 peak_duration=0.1, fade_duration=0.2, audio_device=None):
        super().__init__()
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.peak_threshold = peak_threshold
        self.peak_duration = peak_duration
        self.fade_duration = fade_duration
        self.audio_device = audio_device

    def add_args(self, parser):
        super().add_args(parser)
        parser.add_argument('--sample-rate', type=int, default=44100,
                          help='Audio sample rate (default: 44100)')
        parser.add_argument('--chunk-size', type=int, default=1024,
                          help='Audio chunk size (default: 1024)')
        parser.add_argument('--peak-threshold', type=float, default=0.05,
                          help='Audio peak threshold (0.0-1.0, default: 0.05)')
        parser.add_argument('--peak-duration', type=float, default=0.1,
                          help='Peak flash duration in seconds (default: 0.1)')
        parser.add_argument('--fade-duration', type=float, default=0.2,
                          help='Fade out duration in seconds (default: 0.2)')
        parser.add_argument('--audio-device', type=int, default=None,
                          help='Audio device index (default: auto-detect)')

    def from_args(self, args):
        super().from_args(args)
        self.sample_rate = args.sample_rate
        self.chunk_size = args.chunk_size
        self.peak_threshold = args.peak_threshold
        self.peak_duration = args.peak_duration
        self.fade_duration = args.fade_duration
        self.audio_device = args.audio_device


class AudioEffect(Effect):
    def __init__(self, client, options: AudioOptions):
        super().__init__(client, options)
        self.stream = None
        self.peak_detected = False
        self.peak_start_time = 0
        self.current_color = Colors.BLACK.value
        self.target_color = Colors.BLACK.value
        self.fade_start_time = 0
        self.is_fading = False
        self.lock = threading.Lock()
        self.running = False
    
    @classmethod
    def info(cls):
        """Display information about available audio devices."""
        print("\n=== Audio Device Information ===")
        try:
            devices = sd.query_devices()
            print("Available audio input devices:")
            
            input_devices = []
            for i, device in enumerate(devices):
                # Handle different device dictionary structures
                max_inputs = device.get('max_inputs', 0)
                if max_inputs > 0:
                    device_name = device.get('name', f'Device {i}')
                    sample_rate = device.get('default_samplerate', 'Unknown')
                    print(f"  {i}: {device_name} (inputs: {max_inputs}, sample rates: {sample_rate}Hz)")
                    input_devices.append(i)
            
            if not input_devices:
                print("  No input devices found!")
                print("\nTROUBLESHOOTING:")
                print("• If using Voicemeeter, it may be blocking direct audio device access")
                print("• Try disabling Voicemeeter temporarily to test")
                print("• Check Windows Sound settings to ensure input devices are enabled")
                print("• Make sure you have a microphone or audio input device connected")
            
            # Show default device
            try:
                default_input = sd.default.device[0]
                print(f"\nDefault input device: {default_input}")
                if default_input < len(devices):
                    default_device = devices[default_input]
                    default_name = default_device.get('name', 'Unknown')
                    default_inputs = default_device.get('max_inputs', 0)
                    print(f"Default device info: {default_name} (inputs: {default_inputs})")
                    
                    if default_inputs == 0:
                        print("⚠️  Warning: Default device has no inputs!")
            except Exception as e:
                print(f"Could not determine default device: {e}")
                
        except Exception as e:
            print(f"Error querying audio devices: {e}")
            print("Make sure sounddevice is properly installed and audio drivers are working.")
        
    def _get_default_input_device(self):
        """Get the default input device index."""
        try:
            devices = sd.query_devices()
            
            # First try the default device
            try:
                default_device = sd.default.device[0]
                if default_device < len(devices):
                    device_info = devices[default_device]
                    max_inputs = device_info.get('max_inputs', 0)
                    if max_inputs > 0:
                        return default_device
            except Exception:
                pass
            
            # Search for any device with inputs
            for i, device in enumerate(devices):
                max_inputs = device.get('max_inputs', 0)
                if max_inputs > 0:
                    return i
            
            return None
        except Exception as e:
            print(f"Error getting default input device: {e}")
            return None
    
    def _calculate_rms(self, audio_data):
        """Calculate RMS (Root Mean Square) of audio data without numpy."""
        if not audio_data:
            return 0.0
        
        # Convert to list if it's not already
        if hasattr(audio_data, 'tolist'):
            data = audio_data.tolist()
        else:
            data = list(audio_data)
        
        # Handle multi-dimensional arrays
        if isinstance(data[0], (list, tuple)):
            # Take first channel if stereo
            data = [sample[0] if isinstance(sample, (list, tuple)) else sample for sample in data]
        
        # Calculate RMS
        sum_squares = sum(sample * sample for sample in data)
        mean_square = sum_squares / len(data)
        rms = math.sqrt(mean_square)
        
        return rms
        
    def _audio_callback(self, indata, frames, callback_time, status):
        """Audio callback function for processing audio data."""
        if status:
            print(f"Audio callback status: {status}")
            return
        
        try:
            # Calculate RMS of audio data using pure Python
            rms = self._calculate_rms(indata)
            self._last_rms = rms  # Store for debugging
            
            current_time = time.time()
            
            with self.lock:
                # Check for peak detection
                if rms > self.options.peak_threshold and not self.peak_detected:
                    self.peak_detected = True
                    self.peak_start_time = current_time
                    # Generate random color
                    self.target_color = RGBColor(
                        random.randint(0, 255),
                        random.randint(0, 255),
                        random.randint(0, 255)
                    ).value
                    self.current_color = self.target_color
                    self.is_fading = False
                
                # Check if peak duration has passed
                elif (self.peak_detected and 
                      current_time - self.peak_start_time > self.options.peak_duration):
                    self.peak_detected = False
                    self.fade_start_time = current_time
                    self.is_fading = True
                
                # Handle fading
                if self.is_fading:
                    fade_progress = (current_time - self.fade_start_time) / self.options.fade_duration
                    if fade_progress >= 1.0:
                        self.current_color = Colors.BLACK.value
                        self.is_fading = False
                    else:
                        # Interpolate between target color and black
                        fade_factor = 1.0 - fade_progress
                        self.current_color = RGBColor(
                            int(self.target_color[0] * fade_factor),
                            int(self.target_color[1] * fade_factor),
                            int(self.target_color[2] * fade_factor)
                        ).value
                        
        except Exception as e:
            print(f"Error in audio callback: {e}")
            import traceback
            traceback.print_exc()
    
    def start(self):
        """Start the audio effect."""
        try:
            device = self.options.audio_device
            if device is None:
                device = self._get_default_input_device()
            
            if device is None:
                print("No suitable audio input device found!")
                print("\nTROUBLESHOOTING:")
                print("1. Make sure you have a microphone or audio input device connected")
                print("2. If using Voicemeeter, try disabling it temporarily")
                print("3. Check Windows Sound settings to ensure input devices are enabled")
                print("4. Try running the effect with a specific device number")
                return
            
            print(f"Starting audio effect with device {device}")
            
            # Add device info for debugging
            try:
                devices = sd.query_devices()
                # Ensure device is an integer
                device_index = int(device) if device is not None else None
                
                if device_index is not None and device_index < len(devices):
                    device_info = devices[device_index]
                    device_name = device_info.get('name', 'Unknown')
                    max_inputs = device_info.get('max_inputs', 0)
                    sample_rate = device_info.get('default_samplerate', 'Unknown')
                    
                    print(f"Device info: {device_name}")
                    print(f"Max inputs: {max_inputs}")
                    print(f"Sample rate: {sample_rate}")
                    
                    # Check if device actually has inputs
                    if max_inputs <= 0:
                        print(f"ERROR: Device '{device_name}' has no inputs (max_inputs: {max_inputs})")
                        print("This device cannot be used for audio recording.")
                        print("Try selecting a different audio device or check your audio settings.")
                        return
                        
                elif device_index is not None:
                    print(f"ERROR: Device index {device_index} is out of range (max: {len(devices)-1})")
                    return
                else:
                    print("ERROR: Invalid device index")
                    return
                    
            except (ValueError, TypeError) as e:
                print(f"Could not get device info: Invalid device index '{device}' - {e}")
                return
            except Exception as e:
                print(f"Could not get device info: {e}")
                return
            
            self.running = True
            self.stream = sd.InputStream(
                device=device,
                channels=1,
                samplerate=self.options.sample_rate,
                blocksize=self.options.chunk_size,
                callback=self._audio_callback
            )
            self.stream.start()
            print("Audio stream started successfully!")
            
        except Exception as e:
            print(f"Error starting audio effect: {e}")
            import traceback
            traceback.print_exc()
            self.running = False
    
    def loop(self):
        """Main effect loop."""
        if not self.running:
            return
            
        with self.lock:
            self.set_all_target_devices_color(self.current_color)
    
    def stop(self):
        """Stop the audio effect."""
        self.running = False
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception as e:
                print(f"Error stopping audio stream: {e}")
        
        self.turn_off_target_devices() 