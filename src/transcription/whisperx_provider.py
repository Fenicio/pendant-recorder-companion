"""
WhisperX transcription provider for improved accuracy.
"""

import logging
import os
import whisperx
import torch
from typing import List, Tuple, Optional
from . import TranscriptionProvider
from ..audio.utils import setup_ffmpeg_path


class WhisperXProvider(TranscriptionProvider):
    """Transcription provider using WhisperX for improved accuracy."""

    def __init__(self, model_name: str = "base", device: str = "cuda" if torch.cuda.is_available() else "cpu"):
        """
        Initialize WhisperX provider.

        Args:
            model_name (str): Name of the WhisperX model to use
            device (str): Device to use for inference ("cuda" or "cpu")
        """
        # Setup ffmpeg in PATH for WhisperX (it uses ffmpeg internally)
        if not setup_ffmpeg_path():
            logging.warning("ffmpeg setup failed - WhisperX transcription may fail")

        # Log CUDA information
        logging.info(f"CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            logging.info(f"CUDA device count: {torch.cuda.device_count()}")
            logging.info(f"CUDA device name: {torch.cuda.get_device_name(0)}")
            logging.info(f"CUDA version: {torch.version.cuda}")

        self.model_name = model_name
        self.device = device
        try:
            logging.info(f"Loading WhisperX model: {model_name} on {device}")
            compute_type = "float32" if device == "cpu" else "float16"
            logging.info(f"Using compute type: {compute_type}")
            self.model = whisperx.load_model(model_name, device, compute_type=compute_type)
        except Exception as e:
            logging.error(f"Error loading WhisperX model: {e}")
            logging.warning("Falling back to base model on CPU")
            self.device = "cpu"
            compute_type = "float32" if self.device == "cpu" else "float16"
            self.model = whisperx.load_model("base", "cpu", compute_type=compute_type)
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
        import traceback
        import shutil

        try:
            logging.info("=" * 60)
            logging.info("WhisperX Transcription Debug Information")
            logging.info("=" * 60)
            logging.info(f"Audio file path: {audio_path}")
            logging.info(f"Audio file exists: {os.path.exists(audio_path)}")
            if os.path.exists(audio_path):
                logging.info(f"Audio file size: {os.path.getsize(audio_path)} bytes")
            logging.info(f"Language: {language}")
            logging.info(f"Device: {self.device}")

            # Check ffmpeg availability
            ffmpeg_path = shutil.which('ffmpeg')
            logging.info(f"ffmpeg in PATH: {ffmpeg_path}")

            if not ffmpeg_path:
                logging.error("✗ ffmpeg is NOT in PATH!")
                logging.error("WhisperX requires ffmpeg to be accessible via PATH")
                return None

            # Try to run ffmpeg to verify it works
            try:
                import subprocess
                result = subprocess.run(
                    [ffmpeg_path, '-version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                logging.info(f"ffmpeg test exit code: {result.returncode}")
                if result.returncode == 0:
                    logging.info("✓ ffmpeg is working correctly")
                    # Log first line of version output
                    first_line = result.stdout.split('\n')[0] if result.stdout else "No output"
                    logging.info(f"ffmpeg version: {first_line}")
                else:
                    logging.error(f"✗ ffmpeg test failed: {result.stderr}")
            except Exception as e:
                logging.error(f"✗ Failed to test ffmpeg: {e}")

            # Load audio
            logging.info("Calling whisperx.load_audio()...")
            audio = whisperx.load_audio(audio_path)
            logging.info(f"✓ Audio loaded successfully, shape: {audio.shape if hasattr(audio, 'shape') else 'N/A'}")

            # Transcribe with word-level timestamps
            logging.info("Starting transcription with model...")
            result = self.model.transcribe(audio, language=language)
            logging.info(f"✓ Transcription complete, segments: {len(result.get('segments', []))}")

            # Align whisper output
            logging.info(f"Loading alignment model for language: {language or 'en'}...")
            model_a, metadata = whisperx.load_align_model(language_code=language or "en", device=self.device)
            logging.info("✓ Alignment model loaded")

            logging.info("Aligning transcription...")
            result = whisperx.align(result["segments"], model_a, metadata, audio, self.device)
            logging.info("✓ Alignment complete")

            timestamped_segments = []
            for segment in result["segments"]:
                minutes, seconds = divmod(int(segment['start']), 60)
                timestamp = f"{minutes:02d}:{seconds:02d}"
                timestamped_segments.append((timestamp, segment['text'].strip()))

            logging.info(f"✓ Transcribed {audio_path} successfully using WhisperX")
            logging.info(f"Total segments: {len(timestamped_segments)}")
            logging.info("=" * 60)
            return timestamped_segments

        except Exception as e:
            logging.error("=" * 60)
            logging.error("WhisperX Transcription Error")
            logging.error("=" * 60)
            logging.error(f"Error type: {type(e).__name__}")
            logging.error(f"Error message: {e}")
            logging.error("Full traceback:")
            logging.error(traceback.format_exc())
            logging.error("=" * 60)
            return None

    def name(self) -> str:
        return f"whisperx-{self.model_name}-{self.device}"
