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

    def _ensure_ffmpeg_available(self) -> Optional[str]:
        """
        Ensure ffmpeg is available and return its path.

        This method aggressively sets up ffmpeg by:
        1. Checking if imageio-ffmpeg is installed
        2. Getting the bundled ffmpeg binary path
        3. Adding it to PATH environment variable
        4. Setting additional environment variables
        5. Verifying ffmpeg is accessible

        Returns:
            Path to ffmpeg executable or None if not available
        """
        import shutil
        import sys

        try:
            # Try to import imageio-ffmpeg
            logging.info("Checking for imageio-ffmpeg package...")
            try:
                import imageio_ffmpeg
                logging.info("OK: imageio-ffmpeg is installed")
            except ImportError:
                logging.error("ERROR: imageio-ffmpeg is NOT installed!")
                logging.error("Install it with: pip install imageio-ffmpeg")
                return None

            # Get the ffmpeg executable path
            logging.info("Getting ffmpeg executable path from imageio-ffmpeg...")
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            logging.info(f"imageio-ffmpeg.get_ffmpeg_exe() returned: {ffmpeg_exe}")

            if not ffmpeg_exe or not os.path.exists(ffmpeg_exe):
                logging.error(f"ERROR: ffmpeg binary not found at: {ffmpeg_exe}")
                return None

            logging.info(f"OK: ffmpeg binary exists at: {ffmpeg_exe}")
            logging.info(f"File size: {os.path.getsize(ffmpeg_exe)} bytes")

            # Get the directory containing ffmpeg
            ffmpeg_dir = os.path.dirname(ffmpeg_exe)
            logging.info(f"ffmpeg directory: {ffmpeg_dir}")

            # Add to PATH
            current_path = os.environ.get("PATH", "")
            if ffmpeg_dir not in current_path:
                os.environ["PATH"] = ffmpeg_dir + os.pathsep + current_path
                logging.info(f"Added to PATH: {ffmpeg_dir}")
            else:
                logging.info("Already in PATH")

            # Also set FFMPEG environment variable (some tools check this)
            os.environ["FFMPEG_BINARY"] = ffmpeg_exe
            os.environ["FFMPEG_PATH"] = ffmpeg_exe
            logging.info("Set FFMPEG_BINARY and FFMPEG_PATH environment variables")

            # Verify ffmpeg is now accessible
            ffmpeg_check = shutil.which('ffmpeg')
            logging.info(f"Verification - shutil.which('ffmpeg'): {ffmpeg_check}")

            if ffmpeg_check:
                logging.info("SUCCESS: ffmpeg is accessible in PATH")
                return ffmpeg_check
            else:
                logging.error("ERROR: ffmpeg still not in PATH after setup!")
                # Try using the full path directly
                logging.info(f"Will try using full path: {ffmpeg_exe}")
                return ffmpeg_exe

        except Exception as e:
            logging.error(f"ERROR in _ensure_ffmpeg_available: {e}", exc_info=True)
            return None

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

            # Setup ffmpeg RIGHT BEFORE transcription to ensure it's fresh
            logging.info("Setting up ffmpeg for transcription...")
            ffmpeg_exe = self._ensure_ffmpeg_available()

            if not ffmpeg_exe:
                logging.error("CRITICAL: ffmpeg is NOT available!")
                logging.error("Please install: pip install imageio-ffmpeg")
                logging.error("Then restart the application")
                return None

            logging.info(f"SUCCESS: ffmpeg available at: {ffmpeg_exe}")

            # Try to run ffmpeg to verify it works
            try:
                import subprocess
                result = subprocess.run(
                    [ffmpeg_exe, '-version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                logging.info(f"ffmpeg test exit code: {result.returncode}")
                if result.returncode == 0:
                    logging.info("OK: ffmpeg is working correctly")
                    # Log first line of version output
                    first_line = result.stdout.split('\n')[0] if result.stdout else "No output"
                    logging.info(f"ffmpeg version: {first_line}")
                else:
                    logging.error(f"ERROR: ffmpeg test failed: {result.stderr}")
            except Exception as e:
                logging.error(f"ERROR: Failed to test ffmpeg: {e}")

            # Load audio
            logging.info("Calling whisperx.load_audio()...")
            audio = whisperx.load_audio(audio_path)
            logging.info(f"OK: Audio loaded successfully, shape: {audio.shape if hasattr(audio, 'shape') else 'N/A'}")

            # Transcribe with word-level timestamps
            logging.info("Starting transcription with model...")
            result = self.model.transcribe(audio, language=language)
            logging.info(f"OK: Transcription complete, segments: {len(result.get('segments', []))}")

            # Align whisper output
            logging.info(f"Loading alignment model for language: {language or 'en'}...")
            model_a, metadata = whisperx.load_align_model(language_code=language or "en", device=self.device)
            logging.info("OK: Alignment model loaded")

            logging.info("Aligning transcription...")
            result = whisperx.align(result["segments"], model_a, metadata, audio, self.device)
            logging.info("OK: Alignment complete")

            timestamped_segments = []
            for segment in result["segments"]:
                minutes, seconds = divmod(int(segment['start']), 60)
                timestamp = f"{minutes:02d}:{seconds:02d}"
                timestamped_segments.append((timestamp, segment['text'].strip()))

            logging.info(f"OK: Transcribed {audio_path} successfully using WhisperX")
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
