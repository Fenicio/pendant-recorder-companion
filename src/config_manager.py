import json
import os
import logging

DEFAULT_CONFIG = {
    "obsidian_vault_path": "",  # This will need to be set by the user
    "record_folder_name": "RECORD",
    "media_folder_name": "media",
    "transcription": {
        "provider": "whisperx",
        "language": "en",
        "model": "base"
    },
    "vad": {
        "enabled": False,
        "threshold": 0.5,
        "min_speech_duration_ms": 250,
        "min_silence_duration_ms": 1000,
        "output_folder": "vad_recordings"
    }
}

def ensure_config_exists(config_path='config/config.json'):
    """
    Ensures that a configuration file exists. If it doesn't, creates one with default values.
    
    Args:
        config_path (str): Path to the configuration file
        
    Returns:
        dict: The configuration dictionary
    """
    try:
        # Try to load existing config
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        
        # If config doesn't exist, create directory if needed
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        # Create default config
        with open(config_path, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        logging.info(f"Created default configuration file at {config_path}")
        
        return DEFAULT_CONFIG
        
    except Exception as e:
        logging.error(f"Error handling configuration file: {e}")
        return DEFAULT_CONFIG  # Return default config even if we can't write it

class ConfigManager:
    """Manages configuration for the Pendant Recorder Companion application."""
    
    def __init__(self, config_path='config/config.json'):
        """
        Initialize the ConfigManager.
        
        Args:
            config_path (str): Path to the configuration file
        """
        self.config_path = config_path
        self.config = ensure_config_exists(config_path)
        
    @property
    def vad(self):
        """Get VAD configuration section."""
        return self.config.get('vad', {})
    
    def get(self, key, default=None):
        """
        Get a configuration value.
        
        Args:
            key (str): The configuration key to retrieve
            default: The default value to return if key doesn't exist
            
        Returns:
            The configuration value or default if not found
        """
        return self.config.get(key, default)
    
    def set(self, key, value):
        """
        Set a configuration value and save to file.
        
        Args:
            key (str): The configuration key to set
            value: The value to set
        """
        self.config[key] = value
        self.save()
    
    def save(self):
        """Save the current configuration to file."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            logging.error(f"Error saving configuration: {e}")
