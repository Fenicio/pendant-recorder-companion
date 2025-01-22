"""
Audio Transcriber Module

This module handles audio transcription operations using various providers:
- Whisper
- WhisperX
- Remote API providers
"""

import logging
from typing import Optional
from ..transcription import TranscriptionProvider
from ..transcription.whisper_provider import WhisperProvider
from ..transcription.whisperx_provider import WhisperXProvider
from ..transcription.remote_provider import RemoteProvider
from ..config_manager import ensure_config_exists

class AudioTranscriber:
    """
    Handles audio transcription using configured providers.
    
    This class manages the transcription of audio files to text using
    various transcription providers (Whisper, WhisperX, Remote).
    """
    
    def __init__(self, config_path: str = 'config/config.json'):
        """
        Initialize the transcriber with configured provider.
        
        Args:
            config_path: Path to the configuration file
        """
        self.default_language = "en"
        self.provider = None
        
        # Load configuration
        config = ensure_config_exists(config_path)
        transcription_config = config.get('transcription', {})
        
        # Set up provider based on configuration
        self._setup_provider(transcription_config)
        
    def _setup_provider(self, transcription_config: dict) -> None:
        """
        Set up the transcription provider based on configuration.
        
        Args:
            transcription_config: Transcription configuration dictionary
        """
        provider_type = transcription_config.get('provider', 'whisper')
        self.default_language = transcription_config.get('language', 'en')
        
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
            
    def transcribe(self, audio_path: str, language: Optional[str] = None) -> str:
        """
        Transcribe audio file using configured provider.
        
        Args:
            audio_path: Path to the audio file
            language: Language to use for transcription. If not provided, uses default
            
        Returns:
            Transcribed text
        """
        transcribe_language = language or self.default_language
        return self.provider.transcribe(audio_path, transcribe_language)
