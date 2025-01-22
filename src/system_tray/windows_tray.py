"""
Windows-specific system tray implementation using pystray.
"""
import pystray
from PIL import Image
import threading
import logging

class WindowsSystemTray:
    def __init__(self, stop_callback=None):
        self.stop_callback = stop_callback
        self.icon = None
        self._create_icon()
        
    def _create_icon(self):
        # Create a simple icon (you should replace this with your own icon file)
        image = Image.new('RGB', (64, 64), color='blue')
        
        # Create the menu
        menu = pystray.Menu(
            pystray.MenuItem("Pendant Recorder Companion", lambda: None, enabled=False),
            pystray.MenuItem("Quit", self._quit_action)
        )
        
        # Create the icon
        self.icon = pystray.Icon(
            "pendant-recorder",
            image,
            "Pendant Recorder Companion",
            menu
        )

    def _quit_action(self):
        if self.stop_callback:
            self.stop_callback()
        self.stop()
        
    def run(self):
        """Run the system tray icon."""
        self.icon.run()
        
    def stop(self):
        """Stop the system tray icon."""
        if self.icon:
            self.icon.stop()
            
    def run_detached(self):
        """Run the system tray icon in a separate thread."""
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()
        return thread
