Pendant Recorder Companion
========================

A Python application that automatically processes voice recordings from USB devices and creates transcribed notes in Obsidian.

Description
----------
This application monitors removable drives for a RECORD folder containing WAV files. When such files are found, it:
1. Converts WAV files to MP3 format
2. Transcribes the audio to text
3. Creates a new note in your Obsidian vault with the transcription and link to the audio file

Perfect for voice recording workflows where you want to automatically transcribe and organize recordings in Obsidian.

Setup
-----
1. Install Python 3.8 or higher
2. Install required packages:
   pip install watchdog wmi pywin32 pydub

3. Configure the application:
   - Edit config.json to set your Obsidian vault path
   - Default configuration will be created on first run if none exists

Configuration Details
-------------------
1. Open config.json in a text editor. The file contains:
   {
     "obsidian_vault_path": "C:/Path/To/Your/Vault",
     "record_folder_name": "RECORD"
   }

2. Modify the settings:
   - obsidian_vault_path: Set this to the full path of your Obsidian vault
   - record_folder_name: Change this if you want to monitor a differently named folder
   
3. Save the file and restart the application for changes to take effect

Setting Up as Startup Application
------------------------------
To have the application start automatically when Windows boots:

1. Create a shortcut:
   - Right-click main.py and select "Create shortcut"
   - Rename it to "Pendant Recorder Companion"

2. Add to Windows Startup:
   - Press Win + R
   - Type "shell:startup" and press Enter
   - Copy your shortcut to the opened folder

3. Alternative Method (Run minimized):
   - Create a batch file (startup.bat) with these contents:
     pythonw main.py
   - Create a shortcut to this batch file
   - Place the shortcut in the startup folder

Usage
-----
1. Run the application:
   python main.py

2. The application will:
   - Monitor for USB drives
   - Look for a folder named "RECORD" on any connected USB drive
   - Process any WAV files found in that folder
   - Create notes in your Obsidian vault with transcriptions

3. System Tray Features:
   - The application runs in the system tray
   - Right-click the tray icon for options:
     * Open Obsidian Vault
     * View Logs
     * Exit Application

4. Logging:
   - Application logs are written to usb_monitor.log
   - Check this file for debugging and monitoring processing status

File Structure
-------------
- main.py: Application entry point
- windows_drive_monitor.py: Handles USB drive detection and monitoring
- record_folder_handler.py: Processes WAV files when found
- audio_processor.py: Handles audio conversion and transcription
- obsidian_manager.py: Creates and manages Obsidian notes
- config.json: Configuration settings

Notes
-----
- The application must be running to process new recordings
- Files are processed only once to avoid duplicates
- Supports only WAV files for input
- Creates MP3 files for better compatibility and file size
- When running as a startup application, the window will be hidden in the system tray
- To stop the application, right-click the system tray icon and select "Exit"
