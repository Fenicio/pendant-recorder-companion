"""
OSX Drive Monitor Module

This module handles the detection and monitoring of USB drives for voice recordings on macOS.
It continuously scans for removable drives, checks for RECORD folders, and sets up
file system monitoring for WAV files.

The module uses macOS-specific methods to detect drive changes and the watchdog
library to monitor folders for new files.

Classes:
    OSXDriveMonitor: Main class that handles drive detection and monitoring.
"""

import os
import logging
import json
import time
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from .audio_processor import AudioProcessor
from .obsidian_manager import ObsidianManager
from .record_folder_handler import RecordFolderHandler

class OSXDriveMonitor:
    """
    Monitors macOS drives for RECORD folders containing voice recordings.

    This class continuously scans for removable drives, identifies RECORD folders,
    and sets up file monitoring for WAV files. When files are found, they are
    processed through the audio processor and added to Obsidian.

    Attributes:
        config (dict): Configuration settings loaded from config.json
        audio_processor (AudioProcessor): Handles audio file processing
        obsidian_manager (ObsidianManager): Manages Obsidian note creation
        observers (list): Active watchdog observers
        monitored_drives (set): Currently monitored drive paths
    """

    def __init__(self, config_path="./config/config.json"):
        """Initialize OSX drive monitor with configuration."""
        self.load_config(config_path)
        self.audio_processor = AudioProcessor()
        self.obsidian_manager = ObsidianManager(self.config['obsidian_vault_path'])
        self.observers = []
        self.monitored_drives = set()

    def load_config(self, config_path):
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {
                'obsidian_vault_path': os.path.expanduser('~/Documents/Obsidian/Vault'),
                'record_folder_name': 'RECORD'
            }
            # Save default config
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=4)

    def get_available_drives(self):
        """Get list of currently available mounted volumes."""
        volumes_path = Path("/Volumes")
        return [str(p) for p in volumes_path.iterdir() if p.is_mount()]

    def is_removable_drive(self, drive_path):
        """Check if drive is removable using diskutil."""
        try:
            cmd = ["diskutil", "info", drive_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return "Removable Media: Yes" in result.stdout
        except Exception as e:
            logging.error(f"Error checking drive type for {drive_path}: {e}")
            return False

    def check_drive(self, drive_path):
        """Check if drive contains RECORD folder and start monitoring if found."""
        try:
            record_path = os.path.join(drive_path, self.config['record_folder_name'])
            if os.path.exists(record_path) and drive_path not in self.monitored_drives:
                logging.info(f"Found RECORD folder in {drive_path}")
                self.start_folder_monitoring(record_path)
                self.monitored_drives.add(drive_path)
        except Exception as e:
            logging.error(f"Error checking drive {drive_path}: {e}")

    def start_folder_monitoring(self, folder_path):
        """Start monitoring a RECORD folder for new WAV files."""
        try:
            event_handler = RecordFolderHandler(self.audio_processor, self.obsidian_manager)
            observer = Observer()
            observer.schedule(event_handler, folder_path, recursive=False)
            observer.start()
            self.observers.append(observer)
            logging.info(f"Started monitoring {folder_path}")
        except Exception as e:
            logging.error(f"Error setting up folder monitoring for {folder_path}: {e}")

    def stop_monitoring(self):
        """Stop all file system observers."""
        for observer in self.observers:
            observer.stop()
        for observer in self.observers:
            observer.join()
        self.observers.clear()
        self.monitored_drives.clear()

    def monitor_drives(self):
        """Main loop to continuously monitor for new drives."""
        try:
            while True:
                drives = self.get_available_drives()
                for drive in drives:
                    if self.is_removable_drive(drive):
                        self.check_drive(drive)
                
                # Clean up monitoring for removed drives
                removed_drives = self.monitored_drives - set(drives)
                if removed_drives:
                    logging.info(f"Drives removed: {removed_drives}")
                    self.stop_monitoring()
                
                time.sleep(2)  # Check every 2 seconds
        except KeyboardInterrupt:
            self.stop_monitoring()
