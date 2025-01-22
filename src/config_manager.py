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
