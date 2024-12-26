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
    def __init__(self):
        """Initialize the audio processor with Whisper model."""
        self.model = whisper.load_model("base")

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

    def transcribe_audio(self, audio_path):
        """Transcribe audio file using Whisper."""
        try:
            result = self.model.transcribe(audio_path)
            logging.info(f"Transcribed {audio_path}")
            return result["text"]
        except Exception as e:
            logging.error(f"Error transcribing audio: {e}")
            return None
