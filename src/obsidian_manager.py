"""
Obsidian Manager Module

This module handles the creation and management of notes in an Obsidian vault.
It creates new notes with transcribed content and links to audio files, following
Obsidian's markdown format and conventions.

The module ensures proper file paths and markdown formatting for Obsidian compatibility.
"""

import os
import shutil
import logging
import json
from datetime import datetime
from mutagen.mp3 import MP3
from .config_manager import ensure_config_exists

class ObsidianManager:
    """
    Manages the creation and organization of notes in an Obsidian vault.

    This class handles the creation of new notes in the Obsidian vault, formatting
    the content with proper markdown syntax and including links to audio files.

    Attributes:
        vault_path (str): Path to the Obsidian vault directory
    """
    def __init__(self, vault_path):
        """Initialize Obsidian manager with path to vault."""
        self.vault_path = vault_path
        config = ensure_config_exists()
        self.media_folder = os.path.join(vault_path, config['media_folder_name'])
        os.makedirs(self.media_folder, exist_ok=True)

    def create_note(self, title, content, mp3_path):
        """Create a new note in Obsidian with the transcribed text and MP3 link.
        
        Args:
            title (str): Title of the note
            content (list): List of (timestamp, text) tuples for transcription
            mp3_path (str): Path to the MP3 file
        """
        # Create a sanitized filename for the note
        note_filename = f"{title.replace(' ', '_')}.md"
        note_path = os.path.join(self.vault_path, note_filename)

        # Copy MP3 to media folder
        mp3_filename = os.path.basename(mp3_path)
        new_mp3_path = os.path.join(self.media_folder, mp3_filename)
        shutil.copy2(mp3_path, new_mp3_path)

        # Calculate the duration of the MP3 file
        audio = MP3(new_mp3_path)
        duration = int(audio.info.length)
        duration_minutes, duration_seconds = divmod(duration, 60)

        # Create note content with markdown including duration
        note_content = f"""---
Created: [[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]]
Duration: {duration_minutes}m {duration_seconds}s
---
# {title}

![[{mp3_filename}]]

## Transcription
"""

        # Append timestamped transcription lines
        if content:
            for timestamp, text in content:
                note_content += f"- **{timestamp}**: {text}\n"
        else:
            note_content += "No transcription available.\n"

        # Write the note
        with open(note_path, 'w', encoding='utf-8') as f:
            f.write(note_content)

        logging.info(f"Created Obsidian note: {note_path}")
