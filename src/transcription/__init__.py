"""
Transcription package providing different transcription providers.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
import logging

class TranscriptionProvider(ABC):
    """Base class for transcription providers."""
    
    @abstractmethod
    def transcribe(self, audio_path: str, language: Optional[str] = None) -> Optional[List[Tuple[str, str]]]:
        """
        Transcribe audio file to text with timestamps.
        
        Args:
            audio_path (str): Path to the audio file
            language (str, optional): Language code for transcription
            
        Returns:
            Optional[List[Tuple[str, str]]]: List of (timestamp, text) tuples or None if failed
        """
        pass

    @abstractmethod
    def name(self) -> str:
        """Return the name of the provider."""
        pass
