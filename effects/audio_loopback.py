"""
Advanced Audio effects - listen to system audio output using loopback recording.
"""

import time
import random
import threading
import numpy as np
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
        self.fft_data = None
        
    def _get_loopback_device(self):
        """Get a loopback device for system audio recording."""
        try:
            devices = sd.query_devices()
            # Look for loopback devices (like "Stereo Mix" on Windows)
            for i, device in enumerate(devices):
                if (device['max_inputs'] > 0 and 
                    ('mix' in device['name'].lower() or 
                     'stereo' in device['name'].lower() or
                     'loopback' in device['name'].lower())):
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
                if device['max_inputs'] > 0:
                    return i
            return None
        except Exception as e:
            print(f"Error getting default input device: {e}")
            return None
    
    def _analyze_frequency_bands(self, audio_data):
        """Analyze audio data and return dominant frequency band."""
        try:
            # Perform FFT
            fft = np.fft.fft(audio_data.astype(np.float32))
            freqs = np.fft.fftfreq(len(audio_data), 1.0 / self.options.sample_rate)
            
            # Calculate power in each frequency band
            band_powers = []
            for i in range(len(self.options.frequency_bands) - 1):
                low_freq = self.options.frequency_bands[i]
                high_freq = self.options.frequency_bands[i + 1]
                
                # Find indices for this frequency range
                low_idx = np.argmin(np.abs(freqs - low_freq))
                high_idx = np.argmin(np.abs(freqs - high_freq))
                
                # Calculate power in this band
                power = np.sum(np.abs(fft[low_idx:high_idx]) ** 2)
                band_powers.append(power)
            
            # Find dominant band
            if band_powers:
                dominant_band = np.argmax(band_powers)
                return dominant_band
            
            return 0
            
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
            Colors.PURPLE.value,   # Very high (8000+ Hz)
        ]
        
        if 0 <= band_index < len(colors):
            return colors[band_index]
        else:
            return RGBColor(
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255)
            ).value
    
    def _audio_callback(self, indata, frames, time, status):
        """Audio callback function for processing audio data."""
        if status:
            print(f"Audio callback status: {status}")
            return
        
        try:
            # Calculate RMS of audio data
            audio_data = indata[:, 0] if indata.ndim > 1 else indata
            rms = np.sqrt(np.mean(audio_data.astype(np.float32) ** 2))
            
            current_time = time.time()
            
            with self.lock:
                # Check for peak detection
                if rms > self.options.peak_threshold and not self.peak_detected:
                    self.peak_detected = True
                    self.peak_start_time = current_time
                    
                    # Analyze frequency bands and get color
                    dominant_band = self._analyze_frequency_bands(audio_data)
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