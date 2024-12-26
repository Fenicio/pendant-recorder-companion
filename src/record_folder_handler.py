"""
Record Folder Handler Module

This module handles the processing of WAV files found in RECORD folders. It watches
for new files and processes existing ones, converting them to MP3, transcribing
the audio, and creating Obsidian notes with the transcriptions.

The module uses the watchdog library's event handling system to detect new files
and maintains a set of processed files to avoid duplicates.

Classes:
    RecordFolderHandler: Handles file system events and processes WAV files.
"""

import logging
import os
from datetime import datetime
from watchdog.events import FileSystemEventHandler

class RecordFolderHandler(FileSystemEventHandler):
    """
    Handles file system events for RECORD folders and processes WAV files.

    This class inherits from watchdog's FileSystemEventHandler to receive file
    system events. It processes both existing WAV files when monitoring starts
    and new files as they are created.

    Attributes:
        audio_processor (AudioProcessor): Handles audio conversion and transcription
        obsidian_manager (ObsidianManager): Creates notes in Obsidian
        processed_files (set): Set of files that have been processed
    """
    def __init__(self, audio_processor, obsidian_manager):
        """Initialize handler with audio processor and Obsidian manager."""
        self.audio_processor = audio_processor
        self.obsidian_manager = obsidian_manager
        self.processed_files = set()

    def scan_existing_files(self, folder_path):
        """Scan and process existing WAV files in the folder."""
        logging.info(f"Scanning existing files in {folder_path}")
        for filename in os.listdir(folder_path):
            if filename.lower().endswith('.wav'):
                full_path = os.path.join(folder_path, filename)
                logging.info(f"Found existing WAV file: {full_path}")
                self.process_wav_file(full_path)

    def on_created(self, event):
        """Handle new WAV file creation."""
        if not event.is_directory and event.src_path.lower().endswith('.wav'):
            logging.info(f"New WAV file detected: {event.src_path}")
            if event.src_path not in self.processed_files:
                logging.info(f"Starting to process WAV file: {event.src_path}")
                self.process_wav_file(event.src_path)
            else:
                logging.debug(f"Skipping already processed file: {event.src_path}")

    def parse_datetime_from_filename(self, filename):
        """Parse datetime from filename format REC20241025043932."""
        # Extract the datetime part from the filename (remove 'REC' prefix)
        datetime_str = filename[3:].split('.')[0]
        try:
            # Parse using the format YYYYMMDDhhmmss
            return datetime.strptime(datetime_str, '%Y%m%d%H%M%S')
        except ValueError as e:
            logging.error(f"Failed to parse datetime from filename {filename}: {e}")
            return None

    def process_wav_file(self, wav_path):
        """Process a WAV file: convert to MP3, transcribe, and create note."""
        success = False
        try:
            # Mark file as being processed
            self.processed_files.add(wav_path)
            logging.info(f"Added {wav_path} to processed files set")

            # Get datetime from filename
            filename = os.path.basename(wav_path)
            file_datetime = self.parse_datetime_from_filename(filename)
            if not file_datetime:
                logging.error(f"Could not parse datetime from filename {filename}")
                return

            # Convert to MP3
            logging.info(f"Converting {wav_path} to MP3")
            mp3_path = self.audio_processor.convert_to_mp3(wav_path, file_datetime)
            if not mp3_path:
                logging.error(f"Failed to convert {wav_path} to MP3")
                return

            # Transcribe audio
            logging.info(f"Starting transcription of {mp3_path}")
            transcription = self.audio_processor.transcribe_audio(mp3_path)
            if not transcription:
                logging.error(f"Failed to transcribe {mp3_path}")
                return

            # Create Obsidian note using the datetime from filename
            title = f"Recording_{file_datetime.strftime('%Y%m%d_%H%M%S')}"
            logging.info(f"Creating Obsidian note with title: {title}")
            self.obsidian_manager.create_note(title, transcription, mp3_path)
            logging.info(f"Successfully completed processing of {wav_path}")
            
            # Mark processing as successful
            success = True

        except Exception as e:
            logging.error(f"Error processing WAV file {wav_path}: {str(e)}", exc_info=True)
        finally:
            # Remove from processed set
            self.processed_files.remove(wav_path)
            logging.info(f"Removed {wav_path} from processed files set")
            
            # Delete the original WAV file and MP3 file if processing was successful
            if success:
                try:
                    os.remove(wav_path)
                    logging.info(f"Deleted original WAV file: {wav_path}")
                    os.remove(mp3_path)
                    logging.info(f"Deleted converted MP3 file: {mp3_path}")
                except Exception as e:
                    logging.error(f"Failed to delete files: {str(e)}")
