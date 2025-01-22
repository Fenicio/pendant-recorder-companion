"""
Audio Converter Module

This module handles audio format conversion operations, specifically:
- Converting WAV files to MP3 format
- Managing temporary storage for converted files
- Batch processing of audio files
"""

import logging
import os
from pydub import AudioSegment
from datetime import datetime
from typing import List, Optional

class AudioConverter:
    """
    Handles audio file format conversion operations.
    
    This class is responsible for converting audio files between formats
    and managing the temporary storage of converted files.
    """
    
    def __init__(self):
        """Initialize the audio converter with a temporary directory."""
        self.temp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'temp')
        
        # Create temp directory if it doesn't exist
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
            
    def convert_to_mp3(self, wav_path: str, creation_time: Optional[datetime] = None) -> Optional[str]:
        """
        Convert WAV file to MP3 and store in temp directory.
        
        Args:
            wav_path: Path to the WAV file
            creation_time: The creation time to set for the MP3 file
            
        Returns:
            Path to the created MP3 file in the temp directory, or None if conversion fails
        """
        try:
            audio = AudioSegment.from_wav(wav_path)
            filename = os.path.basename(wav_path)
            mp3_filename = os.path.splitext(filename)[0] + '.mp3'
            mp3_path = os.path.join(self.temp_dir, mp3_filename)
            
            audio.export(mp3_path, format='mp3')
            
            if creation_time:
                timestamp = creation_time.timestamp()
                os.utime(mp3_path, (timestamp, timestamp))
            
            logging.info(f"Converted {wav_path} to MP3 in temp directory")
            return mp3_path
        except Exception as e:
            logging.error(f"Error converting WAV to MP3: {e}")
            return None

    def batch_process_wav_files(self, wav_directory: str) -> List[str]:
        """
        Process all WAV files in a directory to MP3 format.
        
        Args:
            wav_directory: Directory containing WAV files
            
        Returns:
            List of paths to the created MP3 files
        """
        mp3_files = []
        try:
            # Clear temp directory before processing
            self.clear_temp_directory()
            
            # Process all WAV files
            for file in os.listdir(wav_directory):
                if file.endswith('.wav'):
                    wav_path = os.path.join(wav_directory, file)
                    mp3_path = self.convert_to_mp3(wav_path)
                    if mp3_path:
                        mp3_files.append(mp3_path)
            
            logging.info(f"Processed {len(mp3_files)} WAV files to MP3")
            return mp3_files
        except Exception as e:
            logging.error(f"Error in batch processing: {e}")
            return mp3_files
            
    def clear_temp_directory(self) -> None:
        """Clear all MP3 files from the temporary directory."""
        try:
            for file in os.listdir(self.temp_dir):
                if file.endswith('.mp3'):
                    os.remove(os.path.join(self.temp_dir, file))
            logging.info("Cleared temporary directory")
        except Exception as e:
            logging.error(f"Error clearing temp directory: {e}")
