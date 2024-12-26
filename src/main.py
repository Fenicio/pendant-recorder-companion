"""
Main entry point for the Pendant Recorder Companion application.

This script initializes and starts the Windows drive monitoring system that watches
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
from .windows_drive_monitor import WindowsDriveMonitor
from .system_tray import SystemTrayIcon

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('usb_monitor.log'),
        logging.StreamHandler()
    ]
)

class Application:
    def __init__(self):
        self.monitor = None
        self.stop_event = threading.Event()
        self.system_tray = None
        
    def start(self):
        """Start the application components."""
        # Initialize the drive monitor
        self.monitor = WindowsDriveMonitor()
        
        # Initialize system tray
        self.system_tray = SystemTrayIcon(stop_callback=self.stop)
        self.system_tray.run_detached()
        
        # Start monitoring
        self.monitor.monitor_drives()
        
    def stop(self):
        """Stop the application gracefully."""
        logging.info("Shutting down application...")
        if self.monitor:
            # Add any cleanup needed for the monitor
            pass
        if self.system_tray:
            self.system_tray.stop()
        # Exit the application
        sys.exit(0)

def main():
    """Main entry point for the application."""
    app = Application()
    
    # Set up signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        app.stop()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    app.start()

if __name__ == "__main__":
    main()