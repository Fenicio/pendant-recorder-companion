import whisperx
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from audio.utils import setup_ffmpeg_path

# Setup ffmpeg in PATH (required for WhisperX)
setup_ffmpeg_path()

# This will trigger the model download if it hasn't been downloaded yet
model = whisperx.load_model("base", device="cpu", compute_type="int8")
print("Model loaded successfully!")
