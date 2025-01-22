"""
macOS-specific system tray (menu bar) implementation using rumps.
"""
import rumps
import threading
import logging

class OSXSystemTray(rumps.App):
    def __init__(self, stop_callback=None):
        super().__init__("Pendant Recorder")
        self.stop_callback = stop_callback
        self.icon = None  # Should be replaced with actual icon
        self._setup_menu()
        
    def _setup_menu(self):
        """Set up the menu bar items."""
        self.menu = ["Quit"]
        
    @rumps.clicked("Quit")
    def _quit_action(self, _):
        """Handle quit action."""
        if self.stop_callback:
            self.stop_callback()
        rumps.quit_application()
        
    def run(self):
        """Run the menu bar app."""
        self.run()
        
    def stop(self):
        """Stop the menu bar app."""
        rumps.quit_application()
            
    def run_detached(self):
        """Run the menu bar app in a separate thread."""
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()
        return thread
