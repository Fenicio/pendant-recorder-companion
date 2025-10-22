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


def setup_ffmpeg_path() -> bool:
    """
    Add ffmpeg to system PATH environment variable.

    This is required for libraries like WhisperX and openai-whisper that
    use ffmpeg internally but don't provide a way to configure the path.

    Returns:
        True if ffmpeg was found and added to PATH, False otherwise
    """
    try:
        logging.info("=" * 60)
        logging.info("Setting up ffmpeg PATH configuration")
        logging.info("=" * 60)

        # Log current PATH
        current_path = os.environ.get("PATH", "")
        logging.info(f"Current PATH length: {len(current_path)} characters")
        logging.info(f"Current PATH directories: {current_path.count(os.pathsep)} entries")

        # First, try to get ffmpeg from imageio-ffmpeg
        try:
            logging.info("Attempting to import imageio-ffmpeg...")
            import imageio_ffmpeg
            logging.info("imageio-ffmpeg imported successfully")

            ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
            logging.info(f"imageio-ffmpeg.get_ffmpeg_exe() returned: {ffmpeg_path}")

            if ffmpeg_path and os.path.exists(ffmpeg_path):
                logging.info(f"ffmpeg binary exists at: {ffmpeg_path}")
                logging.info(f"ffmpeg binary is executable: {os.access(ffmpeg_path, os.X_OK)}")

                # Add the directory containing ffmpeg to PATH
                ffmpeg_dir = os.path.dirname(ffmpeg_path)
                logging.info(f"ffmpeg directory: {ffmpeg_dir}")

                if ffmpeg_dir not in os.environ.get("PATH", ""):
                    os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
                    logging.info(f"Added ffmpeg directory to PATH: {ffmpeg_dir}")
                else:
                    logging.info(f"ffmpeg directory already in PATH: {ffmpeg_dir}")

                # Verify ffmpeg is accessible
                import shutil
                ffmpeg_check = shutil.which('ffmpeg')
                logging.info(f"shutil.which('ffmpeg') returns: {ffmpeg_check}")

                if ffmpeg_check:
                    logging.info("OK: ffmpeg is accessible in PATH")
                    logging.info("=" * 60)
                    return True
                else:
                    logging.warning("ERROR: ffmpeg not found in PATH after adding directory!")

        except ImportError as e:
            logging.warning(f"imageio-ffmpeg not available: {e}")
        except Exception as e:
            logging.warning(f"Could not setup imageio-ffmpeg PATH: {e}", exc_info=True)

        # Check if ffmpeg is already in PATH
        import shutil
        system_ffmpeg = shutil.which('ffmpeg')
        if system_ffmpeg:
            logging.info(f"OK: System ffmpeg found in PATH: {system_ffmpeg}")
            logging.info("=" * 60)
            return True

        # Try to add custom bundled ffmpeg to PATH
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

        logging.info(f"Checking custom bin directory in: {base_dir}")
        bin_dir = os.path.join(base_dir, 'bin')
        logging.info(f"Custom bin directory path: {bin_dir}")
        logging.info(f"Custom bin directory exists: {os.path.exists(bin_dir)}")

        if os.path.exists(bin_dir):
            if bin_dir not in os.environ.get("PATH", ""):
                os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")
                logging.info(f"Added custom bin directory to PATH: {bin_dir}")

            # Verify ffmpeg is now accessible
            if shutil.which('ffmpeg'):
                logging.info("OK: ffmpeg accessible after adding custom bin directory")
                logging.info("=" * 60)
                return True

        logging.error("ERROR: ffmpeg not found anywhere!")
        logging.error("Please install: pip install imageio-ffmpeg")
        logging.info("=" * 60)
        return False

    except Exception as e:
        logging.error(f"Error setting up ffmpeg PATH: {e}", exc_info=True)
        logging.info("=" * 60)
        return False
