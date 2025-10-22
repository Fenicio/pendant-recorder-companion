"""
Local Whisper transcription provider.
"""

import logging
import whisper
from typing import List, Tuple, Optional
from . import TranscriptionProvider
from ..audio.utils import setup_ffmpeg_path

class WhisperProvider(TranscriptionProvider):
    """Transcription provider using OpenAI's Whisper model locally."""

    def __init__(self, model_name: str = "base"):
        """
        Initialize Whisper provider.

        Args:
            model_name (str): Name of the Whisper model to use
        """
        # Setup ffmpeg in PATH for Whisper (it uses ffmpeg internally)
        if not setup_ffmpeg_path():
            logging.warning("ffmpeg setup failed - Whisper transcription may fail")

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
        import traceback
        import shutil
        import os

        try:
            logging.info("=" * 60)
            logging.info("Whisper Transcription Debug Information")
            logging.info("=" * 60)
            logging.info(f"Audio file path: {audio_path}")
            logging.info(f"Audio file exists: {os.path.exists(audio_path)}")
            if os.path.exists(audio_path):
                logging.info(f"Audio file size: {os.path.getsize(audio_path)} bytes")
            logging.info(f"Language: {language}")
            logging.info(f"Model: {self.model_name}")

            # Check ffmpeg availability
            ffmpeg_path = shutil.which('ffmpeg')
            logging.info(f"ffmpeg in PATH: {ffmpeg_path}")

            if not ffmpeg_path:
                logging.error("✗ ffmpeg is NOT in PATH!")
                logging.error("Whisper requires ffmpeg to be accessible via PATH")
                return None

            logging.info("Starting transcription with model...")
            result = self.model.transcribe(
                audio_path,
                language=language,
                word_timestamps=True
            )
            logging.info(f"✓ Transcription complete, segments: {len(result.get('segments', []))}")

            timestamped_segments = []
            for segment in result.get('segments', []):
                minutes, seconds = divmod(int(segment['start']), 60)
                timestamp = f"{minutes:02d}:{seconds:02d}"
                timestamped_segments.append((timestamp, segment['text'].strip()))

            logging.info(f"✓ Transcribed {audio_path} successfully using Whisper")
            logging.info(f"Total segments: {len(timestamped_segments)}")
            logging.info("=" * 60)
            return timestamped_segments

        except Exception as e:
            logging.error("=" * 60)
            logging.error("Whisper Transcription Error")
            logging.error("=" * 60)
            logging.error(f"Error type: {type(e).__name__}")
            logging.error(f"Error message: {e}")
            logging.error("Full traceback:")
            logging.error(traceback.format_exc())
            logging.error("=" * 60)
            return None

    def name(self) -> str:
        return f"whisper-{self.model_name}"
