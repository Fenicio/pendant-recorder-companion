"""
Remote transcription provider using HTTP API.
"""

import logging
import requests
from typing import List, Tuple, Optional
from . import TranscriptionProvider

class RemoteProvider(TranscriptionProvider):
    """Transcription provider that sends audio to a remote API endpoint."""
    
    def __init__(self, api_url: str, api_key: Optional[str] = None):
        """
        Initialize remote provider.
        
        Args:
            api_url (str): URL of the transcription API
            api_key (str, optional): API key for authentication
        """
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key

    def transcribe(self, audio_path: str, language: Optional[str] = None) -> Optional[List[Tuple[str, str]]]:
        """
        Transcribe audio file using remote API.
        
        Args:
            audio_path (str): Path to the audio file
            language (str, optional): Language code for transcription
            
        Returns:
            Optional[List[Tuple[str, str]]]: List of (timestamp, text) tuples or None if failed
        """
        try:
            # Prepare headers
            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            
            # Prepare data
            data = {'language': language} if language else {}
            
            # Send file
            with open(audio_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(
                    f"{self.api_url}/transcribe",
                    headers=headers,
                    data=data,
                    files=files,
                    timeout=300  # 5 minute timeout
                )
            
            response.raise_for_status()
            result = response.json()
            
            # Process response - assuming similar format to Whisper
            timestamped_segments = []
            for segment in result.get('segments', []):
                minutes, seconds = divmod(int(segment['start']), 60)
                timestamp = f"{minutes:02d}:{seconds:02d}"
                timestamped_segments.append((timestamp, segment['text'].strip()))
            
            logging.info(f"Transcribed {audio_path} using remote API")
            return timestamped_segments
        except Exception as e:
            logging.error(f"Error transcribing audio with remote API: {e}")
            return None

    def name(self) -> str:
        return "remote-api"
