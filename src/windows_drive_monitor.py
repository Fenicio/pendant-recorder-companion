"""
Windows Drive Monitor Module

This module handles the detection and monitoring of USB drives for voice recordings.
It continuously scans for removable drives, checks for RECORD folders, and sets up
file system monitoring for WAV files.

The module uses Windows-specific APIs (via win32api and wmi) to detect drive changes
and the watchdog library to monitor folders for new files.

Classes:
    WindowsDriveMonitor: Main class that handles drive detection and monitoring.
"""

import os
import logging
import win32api
import win32con
import win32file
import wmi
import json
import time
from watchdog.observers import Observer
from .audio_processor import AudioProcessor
from .obsidian_manager import ObsidianManager
from .record_folder_handler import RecordFolderHandler

class WindowsDriveMonitor:
    """
    Monitors Windows drives for RECORD folders containing voice recordings.

    This class continuously scans for removable drives, identifies RECORD folders,
    and sets up file monitoring for WAV files. When files are found, they are
    processed through the audio processor and added to Obsidian.

    Attributes:
        config (dict): Configuration settings loaded from config.json
        wmi: Windows Management Instrumentation interface
        audio_processor (AudioProcessor): Handles audio file processing
        obsidian_manager (ObsidianManager): Manages Obsidian note creation
        observers (list): Active watchdog observers
        monitored_drives (set): Currently monitored drive letters
    """

    def __init__(self, config_path="./config/config.json"):
        """Initialize Windows drive monitor with configuration."""
        self.load_config(config_path)
        self.wmi = wmi.WMI()
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
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=4)

    def get_available_drives(self):
        """Get list of currently available drive letters."""
        drives = []
        bitmask = win32api.GetLogicalDrives()
        for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            if bitmask & 1:
                drives.append(f"{letter}:")
            bitmask >>= 1
        return drives

    def is_removable_drive(self, drive):
        """Check if drive is removable."""
        try:
            drive_type = win32file.GetDriveType(drive + "\\")
            return drive_type == win32con.DRIVE_REMOVABLE
        except Exception as e:
            logging.error(f"Error checking drive type for {drive}: {e}")
            return False

    def check_drive(self, drive):
        """Check if drive contains RECORD folder and start monitoring if found."""
        try:
            record_path = os.path.join(drive + "\\", self.config['record_folder_name'])
            if os.path.exists(record_path) and drive not in self.monitored_drives:
                logging.info(f"Found RECORD folder in {drive}")
                self.start_folder_monitoring(record_path)
                self.monitored_drives.add(drive)
        except Exception as e:
            logging.error(f"Error checking drive {drive}: {e}")

    def start_folder_monitoring(self, folder_path):
        """Start monitoring a RECORD folder for new WAV files."""
        try:
            event_handler = RecordFolderHandler(self.audio_processor, self.obsidian_manager)
            # Scan existing files before starting to monitor
            event_handler.scan_existing_files(folder_path)
            
            observer = Observer()
            observer.schedule(event_handler, folder_path, recursive=False)
            observer.start()
            self.observers.append(observer)
            logging.info(f"Started monitoring {folder_path}")
        except Exception as e:
            logging.error(f"Error starting folder monitoring: {e}")

    def monitor_drives(self):
        """Monitor for new drives and check for RECORD folders."""
        while True:
            try:
                current_drives = set()
                for drive in self.get_available_drives():
                    if self.is_removable_drive(drive):
                        current_drives.add(drive)
                        self.check_drive(drive)

                # Remove monitoring for drives that are no longer available
                removed_drives = self.monitored_drives - current_drives
                for drive in removed_drives:
                    self.monitored_drives.remove(drive)
                    logging.info(f"Drive {drive} removed")

            except Exception as e:
                logging.error(f"Error in drive monitoring loop: {e}")
            finally:
                time.sleep(1)  # Check every second
