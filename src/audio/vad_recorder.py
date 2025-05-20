"""
Voice Activity Detection (VAD) recorder using Silero VAD.

This module provides functionality to continuously monitor audio input
and record when speech is detected using Silero VAD.
"""

import torch
import numpy as np
import sounddevice as sd
import soundfile as sf
import threading
import queue
import logging
import os
from datetime import datetime
from pathlib import Path
import wave
import io
from pydub import AudioSegment

class VADRecorder:
    def __init__(self, config, obsidian_manager):
        """
        Initialize VAD recorder.
        
        Args:
            config: Configuration object containing VAD settings
            obsidian_manager: ObsidianManager instance for file management
        """
        self.config = config
        self.obsidian_manager = obsidian_manager
        self.recording = False
        self.audio_queue = queue.Queue()
        self.vad_thread = None
        self.stop_event = threading.Event()
        
        # Load Silero VAD model
        self.model, _ = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                                     model='silero_vad',
                                     force_reload=False)
        self.model.eval()
        
        # Audio settings
        self.sample_rate = 16000
        self.channels = 1
        self.dtype = np.float32
        
        # VAD settings from config
        self.threshold = self.config.vad.get('threshold', 0.5)
        self.min_speech_duration = self.config.vad.get('min_speech_duration_ms', 250)
        self.min_silence_duration = self.config.vad.get('min_silence_duration_ms', 1000)
        
    def audio_callback(self, indata, frames, time, status):
        """Callback for audio stream to process incoming audio data."""
        if status:
            logging.warning(f"Audio callback status: {status}")
        if self.recording:
            self.audio_queue.put(indata.copy())
            
    def process_audio(self):
        """Process audio data using Silero VAD."""
        buffer = []
        speech_detected = False
        silence_duration = 0
        
        while not self.stop_event.is_set():
            try:
                audio_chunk = self.audio_queue.get(timeout=1)
                buffer.append(audio_chunk)
                
                # Convert audio to format expected by Silero VAD
                audio_tensor = torch.FloatTensor(audio_chunk.flatten())
                
                # Get speech probability
                speech_prob = self.model(audio_tensor, self.sample_rate).item()
                
                if speech_prob > self.threshold:
                    if not speech_detected:
                        speech_detected = True
                        silence_duration = 0
                        logging.info("Speech detected, starting recording")
                else:
                    if speech_detected:
                        silence_duration += len(audio_chunk) / self.sample_rate * 1000
                        
                        if silence_duration > self.min_silence_duration:
                            # Save the recording
                            self.save_recording(buffer)
                            buffer = []
                            speech_detected = False
                            silence_duration = 0
                            
            except queue.Empty:
                continue
            except Exception as e:
                logging.error(f"Error processing audio: {e}")
                
    def save_recording(self, buffer):
        """Save the recorded audio buffer as MP3."""
        try:
            # Combine all audio chunks
            audio_data = np.concatenate(buffer)
            
            # Create WAV in memory
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(self.channels)
                wav_file.setsampwidth(2)  # 16-bit audio
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes((audio_data * 32767).astype(np.int16).tobytes())
            
            # Convert to MP3
            wav_buffer.seek(0)
            audio_segment = AudioSegment.from_wav(wav_buffer)
            
            # Generate filename and path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"vad_recording_{timestamp}.mp3"
            
            # Save in Obsidian vault
            vad_folder = Path(self.obsidian_manager.vault_path) / self.config.vad['output_folder']
            vad_folder.mkdir(exist_ok=True)
            
            mp3_path = vad_folder / filename
            audio_segment.export(mp3_path, format="mp3")
            
            # Create or append to daily TTS file
            self.obsidian_manager.process_vad_recording(str(mp3_path))
            
            logging.info(f"Saved recording: {filename}")
            
        except Exception as e:
            logging.error(f"Error saving recording: {e}")
    
    def start(self):
        """Start VAD recording."""
        if not self.config.vad.get('enabled', False):
            logging.info("VAD is disabled in config")
            return
            
        self.recording = True
        self.stop_event.clear()
        
        # Start audio stream
        self.stream = sd.InputStream(
            channels=self.channels,
            samplerate=self.sample_rate,
            dtype=self.dtype,
            callback=self.audio_callback
        )
        self.stream.start()
        
        # Start processing thread
        self.vad_thread = threading.Thread(target=self.process_audio)
        self.vad_thread.start()
        
        logging.info("VAD recorder started")
        
    def stop(self):
        """Stop VAD recording."""
        if self.recording:
            self.recording = False
            self.stop_event.set()
            
            if hasattr(self, 'stream'):
                self.stream.stop()
                self.stream.close()
                
            if self.vad_thread:
                self.vad_thread.join()
                
            logging.info("VAD recorder stopped")
