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
        with open('config.json', 'r') as f:
            config = json.load(f)
        self.media_folder = os.path.join(vault_path, config['media_folder_name'])
        os.makedirs(self.media_folder, exist_ok=True)

    def create_note(self, title, content, mp3_path):
        """Create a new note in Obsidian with the transcribed text and MP3 link."""
        # Create a sanitized filename for the note
        note_filename = f"{title.replace(' ', '_')}.md"
        note_path = os.path.join(self.vault_path, note_filename)

        # Copy MP3 to media folder
        mp3_filename = os.path.basename(mp3_path)
        new_mp3_path = os.path.join(self.media_folder, mp3_filename)
        shutil.copy2(mp3_path, new_mp3_path)

        # Create note content with markdown
        note_content = f"""# {title}

![[{mp3_filename}]]

## Transcription
{content}

---
Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        # Write the note
        with open(note_path, 'w', encoding='utf-8') as f:
            f.write(note_content)

        logging.info(f"Created Obsidian note: {note_path}")
