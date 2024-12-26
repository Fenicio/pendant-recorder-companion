# Pendant Recorder Companion

A Python application that automatically processes voice recordings from USB devices and creates transcribed notes in Obsidian.

## Description
This application monitors removable drives for a `RECORD` folder containing WAV files. When such files are found, it:
1. Converts WAV files to MP3 format
2. Transcribes the audio to text
3. Creates a new note in your Obsidian vault with the transcription and link to the audio file

Perfect for voice recording workflows where you want to automatically transcribe and organize recordings in Obsidian.

## Setup
1. Install Python 3.8 or higher
2. Install required packages:
   ```bash
   pip install watchdog wmi pywin32 pydub
   ```
3. Configure the application:
   - Edit `config.json` to set your Obsidian vault path
   - Default configuration will be created on first run if none exists

## Usage
1. Run the application:
   ```bash
   python main.py
   ```

2. The application will:
   - Monitor for USB drives
   - Look for a folder named "RECORD" on any connected USB drive
   - Process any WAV files found in that folder
   - Create notes in your Obsidian vault with transcriptions

3. Logging:
   - Application logs are written to `usb_monitor.log`
   - Check this file for debugging and monitoring processing status

## Project Structure
- `main.py`: Application entry point
- `windows_drive_monitor.py`: Handles USB drive detection and monitoring
- `record_folder_handler.py`: Processes WAV files when found
- `audio_processor.py`: Handles audio conversion and transcription
- `obsidian_manager.py`: Creates and manages Obsidian notes
- `config.json`: Configuration settings

## Configuration
The `config.json` file contains:
- `obsidian_vault_path`: Path to your Obsidian vault
- `record_folder_name`: Name of the folder to monitor (default: "RECORD")

## Notes
- The application must be running to process new recordings
- Files are processed only once to avoid duplicates
- Supports only WAV files for input
- Creates MP3 files for better compatibility and file size
