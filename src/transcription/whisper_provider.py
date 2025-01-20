"""
Local Whisper transcription provider.
"""

import logging
import whisper
from typing import List, Tuple, Optional
from . import TranscriptionProvider

class WhisperProvider(TranscriptionProvider):
    """Transcription provider using OpenAI's Whisper model locally."""
    
    def __init__(self, model_name: str = "base"):
        """
        Initialize Whisper provider.
        
        Args:
            model_name (str): Name of the Whisper model to use
        """
        self.model_name = model_name
        try:
            logging.info(f"Loading Whisper model: {model_name}")
            self.model = whisper.load_model(model_name)
        except Exception as e:
            logging.error(f"Error loading Whisper model: {e}")
            logging.warning("Falling back to base model")
            self.model = whisper.load_model("base")
            self.model_name = "base"

    def transcribe(self, audio_path: str, language: Optional[str] = None) -> Optional[List[Tuple[str, str]]]:
        """
        Transcribe audio file using Whisper.
        
        Args:
            audio_path (str): Path to the audio file
            language (str, optional): Language code for transcription
            
        Returns:
            Optional[List[Tuple[str, str]]]: List of (timestamp, text) tuples or None if failed
        """
        try:
            result = self.model.transcribe(
                audio_path,
                language=language,
                word_timestamps=True
            )
            
            timestamped_segments = []
            for segment in result.get('segments', []):
                minutes, seconds = divmod(int(segment['start']), 60)
                timestamp = f"{minutes:02d}:{seconds:02d}"
                timestamped_segments.append((timestamp, segment['text'].strip()))
            
            logging.info(f"Transcribed {audio_path} using Whisper")
            return timestamped_segments
        except Exception as e:
            logging.error(f"Error transcribing audio with Whisper: {e}")
            return None

    def name(self) -> str:
        return f"whisper-{self.model_name}"
