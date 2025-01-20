"""
WhisperX transcription provider for improved accuracy.
"""

import logging
import whisperx
import torch
from typing import List, Tuple, Optional
from . import TranscriptionProvider

class WhisperXProvider(TranscriptionProvider):
    """Transcription provider using WhisperX for improved accuracy."""
    
    def __init__(self, model_name: str = "base", device: str = "cuda" if torch.cuda.is_available() else "cpu"):
        """
        Initialize WhisperX provider.
        
        Args:
            model_name (str): Name of the WhisperX model to use
            device (str): Device to use for inference ("cuda" or "cpu")
        """
        self.model_name = model_name
        self.device = device
        try:
            logging.info(f"Loading WhisperX model: {model_name} on {device}")
            self.model = whisperx.load_model(model_name, device)
        except Exception as e:
            logging.error(f"Error loading WhisperX model: {e}")
            logging.warning("Falling back to base model on CPU")
            self.device = "cpu"
            self.model = whisperx.load_model("base", "cpu")
            self.model_name = "base"

    def transcribe(self, audio_path: str, language: Optional[str] = None) -> Optional[List[Tuple[str, str]]]:
        """
        Transcribe audio file using WhisperX.
        
        Args:
            audio_path (str): Path to the audio file
            language (str, optional): Language code for transcription
            
        Returns:
            Optional[List[Tuple[str, str]]]: List of (timestamp, text) tuples or None if failed
        """
        try:
            # Load audio
            audio = whisperx.load_audio(audio_path)
            
            # Transcribe with word-level timestamps
            result = self.model.transcribe(audio, language=language)
            
            # Align whisper output
            model_a, metadata = whisperx.load_align_model(language_code=language or "en", device=self.device)
            result = whisperx.align(result["segments"], model_a, metadata, audio, self.device)
            
            timestamped_segments = []
            for segment in result["segments"]:
                minutes, seconds = divmod(int(segment['start']), 60)
                timestamp = f"{minutes:02d}:{seconds:02d}"
                timestamped_segments.append((timestamp, segment['text'].strip()))
            
            logging.info(f"Transcribed {audio_path} using WhisperX")
            return timestamped_segments
        except Exception as e:
            logging.error(f"Error transcribing audio with WhisperX: {e}")
            return None

    def name(self) -> str:
        return f"whisperx-{self.model_name}-{self.device}"
