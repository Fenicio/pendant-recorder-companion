"""
Unix/Linux system tray implementation using GTK3 via PyGObject.
"""
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, AppIndicator3
import threading
import logging

class UnixSystemTray:
    def __init__(self, stop_callback=None):
        self.stop_callback = stop_callback
        self.indicator = None
        self._create_indicator()
        
    def _create_indicator(self):
        """Create the system tray indicator."""
        self.indicator = AppIndicator3.Indicator.new(
            "pendant-recorder",
            "audio-input-microphone",  # Using a standard icon
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        
        # Create menu
        menu = Gtk.Menu()
        
        # App name item (disabled)
        app_name = Gtk.MenuItem(label="Pendant Recorder Companion")
        app_name.set_sensitive(False)
        menu.append(app_name)
        
        # Separator
        separator = Gtk.SeparatorMenuItem()
        menu.append(separator)
        
        # Quit item
        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", self._quit_action)
        menu.append(quit_item)
        
        menu.show_all()
        self.indicator.set_menu(menu)
        
    def _quit_action(self, _):
        """Handle quit action."""
        if self.stop_callback:
            self.stop_callback()
        Gtk.main_quit()
        
    def run(self):
        """Run the system tray indicator."""
        Gtk.main()
        
    def stop(self):
        """Stop the system tray indicator."""
        Gtk.main_quit()
            
    def run_detached(self):
        """Run the system tray indicator in a separate thread."""
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()
        return thread
