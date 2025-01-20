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
from pydub import AudioSegment
from typing import Optional

from .transcription import TranscriptionProvider
from .transcription.whisper_provider import WhisperProvider
from .transcription.whisperx_provider import WhisperXProvider
from .transcription.remote_provider import RemoteProvider

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
        Initialize the audio processor with configured transcription provider.
        
        Args:
            config_path (str): Path to the configuration file
        """
        # Default configuration
        self.default_language = "en"
        self.provider = None

        # Load configuration if available
        try:
            with open(config_path, 'r') as config_file:
                config = json.load(config_file)
            
            # Get transcription configuration
            transcription_config = config.get('transcription', {})
            provider_type = transcription_config.get('provider', 'whisper')
            self.default_language = transcription_config.get('language', 'en')
            
            # Initialize provider based on configuration
            if provider_type == 'whisperx':
                model = transcription_config.get('model', 'base')
                self.provider = WhisperXProvider(model_name=model)
            elif provider_type == 'remote':
                api_url = transcription_config.get('api_url')
                api_key = transcription_config.get('api_key')
                if not api_url:
                    raise ValueError("Remote provider requires 'api_url' in config")
                self.provider = RemoteProvider(api_url=api_url, api_key=api_key)
            else:  # default to whisper
                model = transcription_config.get('model', 'base')
                self.provider = WhisperProvider(model_name=model)
                
        except FileNotFoundError:
            logging.warning(f"Config file not found at {config_path}. Using default Whisper settings.")
            self.provider = WhisperProvider()
        except json.JSONDecodeError:
            logging.error(f"Error decoding JSON from {config_path}. Using default Whisper settings.")
            self.provider = WhisperProvider()
        except Exception as e:
            logging.error(f"Unexpected error loading config: {e}. Using default Whisper settings.")
            self.provider = WhisperProvider()

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
        Transcribe audio file using configured provider.
        
        Args:
            audio_path (str): Path to the audio file
            language (str, optional): Language to use for transcription. 
                                     If not provided, uses default from config.
        
        Returns:
            list: List of tuples with (timestamp, text) for each segment
        """
        # Use provided language or default from config
        transcribe_language = language or self.default_language
        return self.provider.transcribe(audio_path, transcribe_language)
