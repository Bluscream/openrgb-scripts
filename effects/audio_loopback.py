"""
Advanced Audio effects - listen to system audio output using loopback recording.
"""

import time
import random
import threading
import math
import sounddevice as sd
from classes import Effect, EffectOptions, Colors, RGBColor


class AudioLoopbackOptions(EffectOptions):
    def __init__(self, sample_rate=44100, chunk_size=1024, peak_threshold=0.03, 
                 peak_duration=0.15, fade_duration=0.4, audio_device=None,
                 use_loopback=True, frequency_bands=None):
        super().__init__()
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.peak_threshold = peak_threshold
        self.peak_duration = peak_duration
        self.fade_duration = fade_duration
        self.audio_device = audio_device
        self.use_loopback = use_loopback
        self.frequency_bands = frequency_bands or [60, 250, 500, 2000, 4000, 8000]

    def add_args(self, parser):
        super().add_args(parser)
        parser.add_argument('--sample-rate', type=int, default=44100,
                          help='Audio sample rate (default: 44100)')
        parser.add_argument('--chunk-size', type=int, default=1024,
                          help='Audio chunk size (default: 1024)')
        parser.add_argument('--peak-threshold', type=float, default=0.03,
                          help='Audio peak threshold (0.0-1.0, default: 0.03)')
        parser.add_argument('--peak-duration', type=float, default=0.15,
                          help='Peak flash duration in seconds (default: 0.15)')
        parser.add_argument('--fade-duration', type=float, default=0.4,
                          help='Fade out duration in seconds (default: 0.4)')
        parser.add_argument('--audio-device', type=int, default=None,
                          help='Audio device index (default: auto-detect)')
        parser.add_argument('--use-loopback', action='store_true', default=True,
                          help='Use loopback recording (default: True)')
        parser.add_argument('--frequency-bands', nargs='+', type=int, 
                          default=[60, 250, 500, 2000, 4000, 8000],
                          help='Frequency bands for color mapping (default: 60 250 500 2000 4000 8000)')

    def from_args(self, args):
        super().from_args(args)
        self.sample_rate = args.sample_rate
        self.chunk_size = args.chunk_size
        self.peak_threshold = args.peak_threshold
        self.peak_duration = args.peak_duration
        self.fade_duration = args.fade_duration
        self.audio_device = args.audio_device
        self.use_loopback = args.use_loopback
        self.frequency_bands = args.frequency_bands


class AudioLoopbackEffect(Effect):
    def __init__(self, client, options: AudioLoopbackOptions):
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
        """Display information about available audio devices, including loopback devices."""
        print("\n=== Audio Loopback Device Information ===")
        try:
            devices = sd.query_devices()
            print("Available audio input devices:")
            
            loopback_devices = []
            regular_input_devices = []
            
            for i, device in enumerate(devices):
                # Handle different device dictionary structures
                max_inputs = device.get('max_inputs', 0)
                if max_inputs > 0:
                    device_name = device.get('name', f'Device {i}')
                    sample_rate = device.get('default_samplerate', 'Unknown')
                    device_info = f"  {i}: {device_name} (inputs: {max_inputs}, sample rates: {sample_rate}Hz)"
                    
                    # Check if this looks like a loopback device
                    if ('mix' in device_name.lower() or 
                        'stereo' in device_name.lower() or
                        'loopback' in device_name.lower()):
                        loopback_devices.append((i, device_info))
                    else:
                        regular_input_devices.append((i, device_info))
            
            # Display loopback devices first
            if loopback_devices:
                print("\nLoopback devices (recommended for system audio):")
                for i, device_info in loopback_devices:
                    print(f"  * {device_info}")
            
            # Display regular input devices
            if regular_input_devices:
                print("\nRegular input devices:")
                for i, device_info in regular_input_devices:
                    print(f"  {device_info}")
            
            # Show default device
            try:
                default_device = sd.default.device[0]  # Input device
                print(f"\nDefault input device: {default_device}")
            except Exception as e:
                print(f"\nCould not determine default input device: {e}")
            
            # Provide helpful tips
            print("\nTips:")
            print("  - Use loopback devices (like 'Stereo Mix') to capture system audio output")
            print("  - On Windows, enable 'Stereo Mix' in Sound settings if not visible")
            print("  - On Linux, use 'Monitor of' devices for loopback recording")
                
        except Exception as e:
            print(f"Error querying audio devices: {e}")
            print("Make sure sounddevice is properly installed and audio drivers are working.")
            print("You can still use the effect with default settings.")
        
    def _get_loopback_device(self):
        """Get a loopback device for system audio recording."""
        try:
            devices = sd.query_devices()
            # Look for loopback devices (like "Stereo Mix" on Windows)
            for i, device in enumerate(devices):
a                max_inputs = device.get('max_inputs', 0)
                device_name = device.get('name', '')
                if (max_inputs > 0 and 
                    ('mix' in device_name.lower() or 
                     'stereo' in device_name.lower() or
                     'loopback' in device_name.lower())):
                    return i
            return None
        except Exception as e:
            print(f"Error getting loopback device: {e}")
            return None
    
    def _get_default_input_device(self):
        """Get the default input device index."""
        try:
            devices = sd.query_devices()
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
    
    def _analyze_frequency_bands(self, audio_data):
        """Analyze audio data and return dominant frequency band using simple amplitude analysis."""
        try:
            # Convert to list if needed
            if hasattr(audio_data, 'tolist'):
                data = audio_data.tolist()
            else:
                data = list(audio_data)
            
            # Handle multi-dimensional arrays
            if isinstance(data[0], (list, tuple)):
                data = [sample[0] if isinstance(sample, (list, tuple)) else sample for sample in data]
            
            # Simple frequency analysis based on amplitude patterns
            # This is a simplified approach without FFT
            data_length = len(data)
            if data_length < 2:
                return 0
            
            # Calculate amplitude variations to estimate frequency content
            # Higher frequency content tends to have more rapid amplitude changes
            amplitude_changes = []
            for i in range(1, data_length):
                change = abs(data[i] - data[i-1])
                amplitude_changes.append(change)
            
            if not amplitude_changes:
                return 0
            
            # Calculate average amplitude change
            avg_change = sum(amplitude_changes) / len(amplitude_changes)
            
            # Simple band detection based on amplitude characteristics
            # This is a rough approximation without proper FFT
            if avg_change < 0.01:
                return 0  # Low frequency (bass)
            elif avg_change < 0.02:
                return 1  # Low-mid
            elif avg_change < 0.03:
                return 2  # Mid
            elif avg_change < 0.04:
                return 3  # High-mid
            elif avg_change < 0.05:
                return 4  # High
            else:
                return 5  # Very high
            
        except Exception as e:
            print(f"Error analyzing frequency bands: {e}")
            return 0
    
    def _get_color_for_frequency_band(self, band_index):
        """Get color based on frequency band."""
        colors = [
            Colors.RED.value,      # Bass (60-250 Hz)
            Colors.ORANGE.value,   # Low-mid (250-500 Hz)
            Colors.YELLOW.value,   # Mid (500-2000 Hz)
            Colors.GREEN.value,    # High-mid (2000-4000 Hz)
            Colors.BLUE.value,     # High (4000-8000 Hz)
            Colors.VIOLET.value,   # Very high (8000+ Hz)
        ]
        
        if 0 <= band_index < len(colors):
            return colors[band_index]
        else:
            return RGBColor(
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255)
            ).value
    
    def _audio_callback(self, indata, frames, callback_time, status):
        """Audio callback function for processing audio data."""
        if status:
            print(f"Audio callback status: {status}")
            return
        
        try:
            # Calculate RMS of audio data using pure Python
            rms = self._calculate_rms(indata)
            
            current_time = time.time()
            
            with self.lock:
                # Check for peak detection
                if rms > self.options.peak_threshold and not self.peak_detected:
                    self.peak_detected = True
                    self.peak_start_time = current_time
                    
                    # Analyze frequency bands and get color
                    dominant_band = self._analyze_frequency_bands(indata)
                    self.target_color = self._get_color_for_frequency_band(dominant_band)
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
    
    def start(self):
        """Start the audio effect."""
        try:
            device = self.options.audio_device
            if device is None:
                if self.options.use_loopback:
                    device = self._get_loopback_device()
                    if device is None:
                        print("No loopback device found, falling back to default input device")
                        device = self._get_default_input_device()
                else:
                    device = self._get_default_input_device()
            
            if device is None:
                print("No suitable audio input device found!")
                return
            
            print(f"Starting audio loopback effect with device {device}")
            
            self.running = True
            self.stream = sd.InputStream(
                device=device,
                channels=1,
                samplerate=self.options.sample_rate,
                blocksize=self.options.chunk_size,
                callback=self._audio_callback
            )
            self.stream.start()
            
        except Exception as e:
            print(f"Error starting audio effect: {e}")
    
    def loop(self):
        """Main effect loop."""
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