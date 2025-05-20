"""
Main entry point for the Pendant Recorder Companion application.

This script initializes and starts the platform-specific drive monitoring system that watches
for USB drives containing voice recordings. It sets up logging and launches the
main monitoring loop with a system tray icon.

Usage:
    python main.py

The application will run continuously, monitoring for USB drives and processing
any WAV files found in RECORD folders on those drives.
"""

import logging
import threading
import signal
import sys
from .factories import DriveMonitorFactory, SystemTrayFactory
from .audio.vad_recorder import VADRecorder
from .config_manager import ConfigManager
from .obsidian_manager import ObsidianManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('pendant_recorder.log')
    ]
)

class Application:
    def __init__(self):
        self.monitor = None
        self.stop_event = threading.Event()
        self.system_tray = None
        self.vad_recorder = None
        
        # Initialize managers
        self.config_manager = ConfigManager()
        self.obsidian_manager = ObsidianManager(self.config_manager.get('obsidian_vault_path'))
        
    def start(self):
        """Start the application components."""
        try:
            # Initialize the platform-specific drive monitor
            self.monitor = DriveMonitorFactory.create_monitor()
            
            # Initialize platform-specific system tray
            self.system_tray = SystemTrayFactory.create_tray(stop_callback=self.stop)
            self.system_tray.run_detached()
            
            # Initialize and start VAD recorder if enabled
            self.vad_recorder = VADRecorder(self.config_manager, self.obsidian_manager)
            self.vad_recorder.start()
            
            # Start monitoring
            self.monitor.monitor_drives()
        except Exception as e:
            logging.error(f"Failed to start application: {e}")
            logging.exception("Detailed error traceback:")
            self.stop()
        
    def stop(self):
        """Stop the application gracefully."""
        try:
            logging.info("Shutting down application...")
            if self.monitor:
                self.monitor.stop()
            if self.system_tray:
                self.system_tray.stop()
            if self.vad_recorder:
                self.vad_recorder.stop()
            # Exit the application
            sys.exit(0)
        except Exception as e:
            logging.error(f"Error during application shutdown: {e}")
            logging.exception("Detailed shutdown error traceback:")
            sys.exit(1)

def signal_handler(signum, frame):
    """Handle system signals for graceful shutdown."""
    app.stop()

def main():
    """Initialize and run the Pendant Recorder Companion application."""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    app = Application()
    app.start()

if __name__ == "__main__":
    main()