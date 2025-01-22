"""
Factory classes for creating platform-specific implementations of drive monitors
and system tray icons.
"""
import sys
import platform
import logging

class DriveMonitorFactory:
    """Factory for creating platform-specific drive monitor instances."""
    
    @staticmethod
    def create_monitor(config_path="./config/config.json"):
        """
        Create and return a drive monitor instance appropriate for the current platform.
        
        Args:
            config_path (str): Path to configuration file
            
        Returns:
            A platform-specific drive monitor instance
        
        Raises:
            ImportError: If required platform-specific dependencies are not available
            RuntimeError: If the platform is not supported
        """
        system = platform.system().lower()
        
        try:
            if system == 'windows':
                from .windows_drive_monitor import WindowsDriveMonitor
                return WindowsDriveMonitor(config_path)
            elif system == 'darwin':
                from .osx_drive_monitor import OSXDriveMonitor
                return OSXDriveMonitor(config_path)
            elif system == 'linux':
                from .unix_drive_monitor import UnixDriveMonitor
                return UnixDriveMonitor(config_path)
            else:
                raise RuntimeError(f"Unsupported platform: {system}")
        except ImportError as e:
            logging.error(f"Failed to import drive monitor for {system}: {e}")
            logging.error("Please ensure all required dependencies are installed.")
            raise


class SystemTrayFactory:
    """Factory for creating platform-specific system tray instances."""
    
    @staticmethod
    def create_tray(stop_callback=None):
        """
        Create and return a system tray instance appropriate for the current platform.
        
        Args:
            stop_callback (callable): Callback function to be called when stopping the application
            
        Returns:
            A platform-specific system tray instance
        
        Raises:
            ImportError: If required platform-specific dependencies are not available
            RuntimeError: If the platform is not supported
        """
        system = platform.system().lower()
        
        try:
            if system == 'windows':
                from .system_tray.windows_tray import WindowsSystemTray
                return WindowsSystemTray(stop_callback)
            elif system == 'darwin':
                from .system_tray.osx_tray import OSXSystemTray
                return OSXSystemTray(stop_callback)
            elif system == 'linux':
                from .system_tray.unix_tray import UnixSystemTray
                return UnixSystemTray(stop_callback)
            else:
                raise RuntimeError(f"Unsupported platform: {system}")
        except ImportError as e:
            logging.error(f"Failed to import system tray for {system}: {e}")
            logging.error("Please ensure all required dependencies are installed.")
            raise
