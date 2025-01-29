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
   - Edit config/config.json to set your Obsidian vault path
   - Default configuration will be created on first run if none exists

Configuration Details
-------------------
1. Open config/config.json in a text editor. The file contains:
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
   - Right-click run.py and select "Create shortcut"
   - Rename it to "Pendant Recorder Companion"

2. Add to Windows Startup:
   - Press Win + R
   - Type "shell:startup" and press Enter
   - Copy your shortcut to the opened folder

3. Alternative Method (Run minimized):
   - Create a batch file (startup.bat) with these contents:
     pythonw run.py
   - Create a shortcut to this batch file
   - Place the shortcut in the startup folder

Usage
-----
1. Run the application:
   python run.py

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
   - Application logs are written to logs/usb_monitor.log
   - Check this file for debugging and monitoring processing status

Project Structure
-------------
src/
  - main.py: Application entry point and core logic
  - windows_drive_monitor.py: Handles USB drive detection and monitoring
  - record_folder_handler.py: Processes WAV files when found
  - audio_processor.py: Handles audio conversion and transcription
  - obsidian_manager.py: Creates and manages Obsidian notes
  - system_tray.py: System tray interface implementation
config/
  - config.json: Configuration settings
logs/
  - usb_monitor.log: Application logs
run.py: Main entry point script

## FFmpeg Integration

This project includes FFmpeg for audio conversion. The FFmpeg binaries should be placed in the `bin` directory:

```
bin/
  ffmpeg.exe  (Windows)
  ffmpeg      (Linux/Mac)
```

When distributing the application:
1. Download the appropriate FFmpeg binaries for your platform
2. Place them in the `bin` directory
3. The application will automatically use the bundled FFmpeg

For development:
- Windows: Download FFmpeg from https://ffmpeg.org/download.html#build-windows
- Linux: Use your package manager or download from https://ffmpeg.org/download.html
- Mac: Use homebrew (`brew install ffmpeg`) or download from https://ffmpeg.org/download.html

Notes
-----
- The application must be running to process new recordings
- Files are processed only once to avoid duplicates
- Supports only WAV files for input
- Creates MP3 files for better compatibility and file size
- When running as a startup application, the window will be hidden in the system tray
- To stop the application, right-click the system tray icon and select "Exit"

Error Handling
-------------
The application handles various error cases gracefully to ensure continuous operation:

1. WAV to MP3 Conversion Errors:
   - If a WAV file is corrupted or cannot be read:
     * The error is logged
     * The file is skipped
     * Processing continues with the next file
   - If there's insufficient disk space:
     * The conversion is aborted
     * An error message is logged
     * The application continues monitoring for new files

2. Audio Transcription Errors:
   - If the audio file cannot be transcribed:
     * The note is still created
     * A "No transcription available" message is added to the note
     * The audio file link is preserved
   - If the transcription service (Whisper) fails:
     * The error is logged
     * The application retries up to 3 times
     * If all retries fail, proceeds with note creation without transcription

3. Ollama Integration Errors:
   - If Ollama server is unreachable:
     * The original prompt text is preserved in the note
     * The error is logged
     * Note creation continues without Ollama processing
   - If Ollama returns an error:
     * The original prompt text is kept
     * The error response is logged
     * The application continues processing other prompts
   - If the model specified in config doesn't exist:
     * A warning is logged
     * The original prompt is preserved
     * Future prompts will continue to be processed once correct model is available

The application is designed to be resilient - no single error will crash the application or stop it from monitoring for new files. All errors are logged to help with troubleshooting.

Generating the exe
-----------------
1. Install pyinstaller
2. Run this command:
pyinstaller --hidden-import=numba.core.types.old_scalars --hidden-import=numba.core.datamodel.old_models --hidden-import=numba.cpython.old_builtins --hidden-import=numba.core.typing.old_builtins --hidden-import=lightning_fabric --collect-data lightning_fabric --collect-data speechbrain --collect-all speechbrain --collect-data whisperx --collect-all whisperx --collect-all pyannote.audio --add-data "C:\Users\sirgu\miniconda3\Lib\site-packages\whisperx\assets;whisperx\assets" --onefile run.py
3. The exe file will be created in the dist folder


Logging
-------
Can't run conda from the terminal, there's a anaconda navigator app

conda create --name pendant-recorder-companion python=3.10
conda activate pendant-recorder-companion


https://github.com/m-bain/whisperX