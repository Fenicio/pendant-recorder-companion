"""
Audio utilities module for managing ffmpeg dependencies and paths.
"""

import os
import sys
import platform
import logging
import shutil
from typing import Optional

# Global flag to track if pydub has been initialized
_pydub_initialized = False

def get_ffmpeg_path() -> Optional[str]:
    """
    Get the path to the ffmpeg executable.

    Checks in the following order:
    1. imageio-ffmpeg bundled binary (installed via pip)
    2. Custom bundled ffmpeg in bin/ directory
    3. System ffmpeg in PATH

    Returns:
        Path to ffmpeg executable or None if not found
    """
    try:
        # Try to use imageio-ffmpeg bundled binary (recommended)
        try:
            import imageio_ffmpeg
            ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
            if ffmpeg_path and os.path.exists(ffmpeg_path):
                logging.info(f"Using imageio-ffmpeg bundled binary at: {ffmpeg_path}")
                return ffmpeg_path
        except ImportError:
            logging.warning("imageio-ffmpeg not installed, trying other methods")
        except Exception as e:
            logging.warning(f"Could not get ffmpeg from imageio-ffmpeg: {e}")

        # Get the base directory of the application
        if getattr(sys, 'frozen', False):
            # If running as a bundled executable
            base_dir = os.path.dirname(sys.executable)
        else:
            # If running from source
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

        # Check for custom bundled ffmpeg binary
        if platform.system().lower() == 'windows':
            ffmpeg_path = os.path.join(base_dir, 'bin', 'ffmpeg.exe')
        else:
            ffmpeg_path = os.path.join(base_dir, 'bin', 'ffmpeg')

        if os.path.exists(ffmpeg_path):
            logging.info(f"Found custom bundled ffmpeg at: {ffmpeg_path}")
            return ffmpeg_path

        # Try to find system ffmpeg in PATH
        system_ffmpeg = shutil.which('ffmpeg')
        if system_ffmpeg:
            logging.info(f"Found system ffmpeg at: {system_ffmpeg}")
            return system_ffmpeg

        # ffmpeg not found anywhere
        logging.error(
            "ffmpeg not found! Please install dependencies:\n"
            "  pip install imageio-ffmpeg\n"
            "  Or install system ffmpeg:\n"
            "    Windows: winget install ffmpeg\n"
            "    macOS: brew install ffmpeg\n"
            "    Linux: sudo apt install ffmpeg"
        )
        return None

    except Exception as e:
        logging.error(f"Error getting ffmpeg path: {e}")
        return None


def initialize_pydub() -> bool:
    """
    Initialize pydub with ffmpeg paths.

    This should be called once at application startup to configure
    pydub to use the bundled or system ffmpeg.

    Returns:
        True if ffmpeg was found and pydub was configured, False otherwise
    """
    global _pydub_initialized

    if _pydub_initialized:
        return True

    try:
        from pydub import AudioSegment

        ffmpeg_path = get_ffmpeg_path()
        if ffmpeg_path:
            AudioSegment.converter = ffmpeg_path
            AudioSegment.ffmpeg = ffmpeg_path

            # Also try to set ffprobe path
            ffprobe_path = ffmpeg_path.replace('ffmpeg', 'ffprobe')
            if os.path.exists(ffprobe_path):
                AudioSegment.ffprobe = ffprobe_path

            _pydub_initialized = True
            logging.info("pydub initialized successfully with ffmpeg")
            return True
        else:
            logging.error("Failed to initialize pydub: ffmpeg not found")
            return False

    except Exception as e:
        logging.error(f"Error initializing pydub: {e}")
        return False
