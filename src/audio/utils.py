"""
Audio utilities module for managing ffmpeg dependencies and paths.
"""

import os
import sys
import platform
import logging
from typing import Optional

def get_ffmpeg_path() -> Optional[str]:
    """
    Get the path to the bundled ffmpeg executable.
    
    Returns:
        Path to ffmpeg executable or None if not found
    """
    try:
        # Get the base directory of the application
        if getattr(sys, 'frozen', False):
            # If running as a bundled executable
            base_dir = os.path.dirname(sys.executable)
        else:
            # If running from source
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        
        # Construct path to ffmpeg binary
        if platform.system().lower() == 'windows':
            ffmpeg_path = os.path.join(base_dir, 'bin', 'ffmpeg.exe')
        else:
            ffmpeg_path = os.path.join(base_dir, 'bin', 'ffmpeg')
            
        if os.path.exists(ffmpeg_path):
            return ffmpeg_path
        else:
            logging.warning(f"Bundled ffmpeg not found at {ffmpeg_path}")
            return None
            
    except Exception as e:
        logging.error(f"Error getting ffmpeg path: {e}")
        return None
