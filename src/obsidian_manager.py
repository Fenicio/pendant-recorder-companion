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
import re
import requests
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
        self.config = ensure_config_exists()
        self.media_folder = os.path.join(vault_path, self.config['media_folder_name'])
        os.makedirs(self.media_folder, exist_ok=True)
        self.template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'note_template.md')

    def process_ollama_prompts(self, content):
        """Process any Ollama prompts in the content.
        
        Args:
            content (str): The markdown content to process
            
        Returns:
            str: The processed content with Ollama responses
        """
        if not self.config.get('ollama', {}).get('enabled', False):
            return content
            
        ollama_config = self.config.get('ollama', {})
        ollama_url = ollama_config.get('url', 'http://localhost:11434')
        model = ollama_config.get('model', 'mistral')
        
        def replace_prompt(match):
            prompt = match.group(1)
            try:
                response = requests.post(
                    f"{ollama_url}/api/generate",
                    json={
                        "model": model,
                        "prompt": f"Context:\n{content}\n\nInstruction: {prompt}",
                        "stream": False
                    }
                )
                if response.status_code == 200:
                    result = response.json()
                    return f"\n\n**Ollama Response**:\n{result['response']}\n\n"
                else:
                    logging.error(f"Failed to get Ollama response: {response.text}")
                    return match.group(0)
            except Exception as e:
                logging.error(f"Error processing Ollama prompt: {e}")
                return match.group(0)
        
        # Find and replace all prompts in double curly braces
        return re.sub(r'\{\{(.*?)\}\}', replace_prompt, content)

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

        # Generate transcription content
        transcription_content = ""
        if content:
            for timestamp, text in content:
                transcription_content += f"- **{timestamp}**: {text}\n"
        else:
            transcription_content = "No transcription available.\n"

        # Read and fill the template
        try:
            with open(self.template_path, 'r', encoding='utf-8') as f:
                template = f.read()
        except FileNotFoundError:
            # Fallback to default template if file doesn't exist
            template = """---
Created: [[{created_datetime}]]
Duration: {duration_minutes}m {duration_seconds}s
---
# {title}

![[{audio_filename}]]

## Transcription
{transcription_content}"""

        # Fill the template
        note_content = template.format(
            created_datetime=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            duration_minutes=duration_minutes,
            duration_seconds=duration_seconds,
            title=title,
            audio_filename=mp3_filename,
            transcription_content=transcription_content
        )

        # Process any Ollama prompts in the content
        note_content = self.process_ollama_prompts(note_content)

        # Write the note
        with open(note_path, 'w', encoding='utf-8') as f:
            f.write(note_content)

        logging.info(f"Created Obsidian note: {note_path}")
