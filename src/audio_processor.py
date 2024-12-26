"""
Audio Processor Module

This module handles all audio-related processing tasks, including:
- Converting WAV files to MP3 format for better compatibility and file size
- Transcribing audio content to text using speech recognition
- Managing audio file operations and conversions

The module uses external libraries for audio processing and speech recognition
to handle the conversion and transcription workflow.
"""

import logging
import os
import json
import whisper
from pydub import AudioSegment

class AudioProcessor:
    """
    Handles audio file processing and transcription.

    This class provides methods for converting audio files between formats
    and transcribing audio content to text. It manages the complete audio
    processing workflow from WAV input to MP3 conversion and text transcription.

    Methods:
        convert_to_mp3: Converts WAV files to MP3 format
        transcribe_audio: Converts audio content to text
    """
    def __init__(self, config_path='config/config.json'):
        """
        Initialize the audio processor with Whisper model from config.
        
        Args:
            config_path (str): Path to the configuration file
        """
        # Default configuration
        self.default_model = "base"
        self.default_language = "en"

        # Load additional Whisper configuration if available
        try:
            with open(config_path, 'r') as config_file:
                config = json.load(config_file)
                
            # Check for Whisper-specific configuration
            whisper_config = config.get('whisper', {})
            model_name = whisper_config.get('model', self.default_model)
            language = whisper_config.get('language', self.default_language)
            
            # Update class attributes
            self.default_model = model_name
            self.default_language = language
        except FileNotFoundError:
            logging.warning(f"Config file not found at {config_path}. Using default Whisper settings.")
        except json.JSONDecodeError:
            logging.error(f"Error decoding JSON from {config_path}. Using default Whisper settings.")
        except Exception as e:
            logging.error(f"Unexpected error loading config: {e}. Using default Whisper settings.")

        # Load Whisper model
        try:
            logging.info(f"Loading Whisper model: {self.default_model}")
            self.model = whisper.load_model(self.default_model)
        except Exception as e:
            logging.error(f"Error loading Whisper model: {e}")
            # Fallback to absolute default
            logging.warning("Falling back to absolute default Whisper model")
            self.model = whisper.load_model("base")
            self.default_model = "base"
            self.default_language = "en"

    def convert_to_mp3(self, wav_path, creation_time=None):
        """
        Convert WAV file to MP3 and set the correct creation time metadata.
        
        Args:
            wav_path (str): Path to the WAV file
            creation_time (datetime): The creation time to set for the MP3 file
        """
        try:
            audio = AudioSegment.from_wav(wav_path)
            mp3_path = wav_path.rsplit('.', 1)[0] + '.mp3'
            audio.export(mp3_path, format='mp3')
            
            # Set the file creation and modification times if provided
            if creation_time:
                timestamp = creation_time.timestamp()
                os.utime(mp3_path, (timestamp, timestamp))
            
            logging.info(f"Converted {wav_path} to MP3")
            return mp3_path
        except Exception as e:
            logging.error(f"Error converting WAV to MP3: {e}")
            return None

    def transcribe_audio(self, audio_path, language=None):
        """
        Transcribe audio file using Whisper.
        
        Args:
            audio_path (str): Path to the audio file
            language (str, optional): Language to use for transcription. 
                                     If not provided, uses default from config.
        
        Returns:
            list: List of tuples with (timestamp, text) for each segment
        """
        try:
            # Use provided language or default from config
            transcribe_language = language or self.default_language
            
            result = self.model.transcribe(
                audio_path, 
                language=transcribe_language,
                word_timestamps=True  # Enable word-level timestamps
            )
            
            # Process segments with timestamps
            timestamped_segments = []
            for segment in result.get('segments', []):
                # Format timestamp as MM:SS
                minutes, seconds = divmod(int(segment['start']), 60)
                timestamp = f"{minutes:02d}:{seconds:02d}"
                timestamped_segments.append((timestamp, segment['text'].strip()))
            
            logging.info(f"Transcribed {audio_path} in {transcribe_language}")
            return timestamped_segments
        except Exception as e:
            logging.error(f"Error transcribing audio: {e}")
            return None
