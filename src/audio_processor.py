"""
Audio Processor Module

This module coordinates audio processing operations by combining:
- Audio format conversion (WAV to MP3)
- Audio transcription
"""

import logging
from typing import List, Optional
from .audio import AudioConverter, AudioTranscriber

class AudioProcessor:
    """
    Coordinates audio processing operations.
    
    This class orchestrates the complete audio processing workflow by combining
    audio conversion and transcription operations.
    """
    
    def __init__(self, config_path: str = 'config/config.json'):
        """
        Initialize the audio processor with its components.
        
        Args:
            config_path: Path to the configuration file
        """
        self.converter = AudioConverter()
        self.transcriber = AudioTranscriber(config_path)
        
    def process_wav_files(self, wav_directory: str, language: Optional[str] = None) -> List[dict]:
        """
        Process WAV files to transcribed text.
        
        Args:
            wav_directory: Directory containing WAV files
            language: Optional language for transcription
            
        Returns:
            List of dictionaries containing MP3 paths and their transcriptions
        """
        results = []
        
        # First convert all WAV files to MP3
        mp3_files = self.converter.batch_process_wav_files(wav_directory)
        
        # Then transcribe each MP3 file
        for mp3_path in mp3_files:
            try:
                transcription = self.transcriber.transcribe(mp3_path, language)
                results.append({
                    'mp3_path': mp3_path,
                    'transcription': transcription
                })
            except Exception as e:
                logging.error(f"Error transcribing {mp3_path}: {e}")
                results.append({
                    'mp3_path': mp3_path,
                    'error': str(e)
                })
        
        return results

    def convert_to_mp3(self, wav_path: str, file_datetime=None) -> Optional[str]:
        """
        Convert WAV file to MP3.
        
        Args:
            wav_path: Path to the WAV file
            file_datetime: Optional datetime to set for the MP3 file
            
        Returns:
            Path to the created MP3 file, or None if conversion fails
        """
        return self.converter.convert_to_mp3(wav_path, file_datetime)

    def transcribe_audio(self, audio_path: str, language: Optional[str] = None) -> Optional[str]:
        """
        Transcribe an audio file.
        
        Args:
            audio_path: Path to the audio file
            language: Optional language for transcription
            
        Returns:
            Transcribed text, or None if transcription fails
        """
        try:
            return self.transcriber.transcribe(audio_path, language)
        except Exception as e:
            logging.error(f"Error transcribing {audio_path}: {e}")
            return None
