"""
Tests for the Voice Activity Detection (VAD) recorder functionality.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
import torch
import threading
import queue
import tempfile
import os
from pathlib import Path
from datetime import datetime

from src.audio.vad_recorder import VADRecorder

class TestVADRecorder(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_config = {
            'vad': {
                'enabled': True,
                'threshold': 0.5,
                'min_speech_duration_ms': 250,
                'min_silence_duration_ms': 1000,
                'output_folder': 'vad_recordings'
            }
        }
        self.mock_obsidian_manager = Mock()
        
        # Create a temporary directory for test outputs
        self.temp_dir = tempfile.mkdtemp()
        self.mock_obsidian_manager.vault_path = self.temp_dir
        
        # Mock the Silero VAD model
        self.mock_model = Mock()
        self.patcher = patch('torch.hub.load')
        self.mock_torch_hub = self.patcher.start()
        self.mock_torch_hub.return_value = (self.mock_model, None)
        
    def tearDown(self):
        """Clean up after each test method."""
        self.patcher.stop()
        # Clean up temporary files
        for file in Path(self.temp_dir).glob('*'):
            file.unlink()
        os.rmdir(self.temp_dir)

    def test_initialization(self):
        """Test VADRecorder initialization."""
        recorder = VADRecorder(self.mock_config, self.mock_obsidian_manager)
        
        self.assertEqual(recorder.threshold, 0.5)
        self.assertEqual(recorder.min_speech_duration, 250)
        self.assertEqual(recorder.min_silence_duration, 1000)
        self.assertFalse(recorder.recording)
        self.assertIsInstance(recorder.audio_queue, queue.Queue)
        
        # Verify Silero VAD model was loaded
        self.mock_torch_hub.assert_called_once_with(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False
        )

    def test_disabled_vad(self):
        """Test that VAD doesn't start when disabled in config."""
        self.mock_config['vad']['enabled'] = False
        recorder = VADRecorder(self.mock_config, self.mock_obsidian_manager)
        
        with patch.object(recorder, 'process_audio') as mock_process:
            recorder.start()
            self.assertFalse(recorder.recording)
            mock_process.assert_not_called()

    @patch('sounddevice.InputStream')
    def test_start_stop(self, mock_input_stream):
        """Test starting and stopping the VAD recorder."""
        mock_stream = MagicMock()
        mock_input_stream.return_value = mock_stream
        
        recorder = VADRecorder(self.mock_config, self.mock_obsidian_manager)
        
        # Test start
        recorder.start()
        self.assertTrue(recorder.recording)
        mock_stream.start.assert_called_once()
        
        # Test stop
        recorder.stop()
        self.assertFalse(recorder.recording)
        mock_stream.stop.assert_called_once()
        mock_stream.close.assert_called_once()

    def test_audio_callback(self):
        """Test audio callback function."""
        recorder = VADRecorder(self.mock_config, self.mock_obsidian_manager)
        recorder.recording = True
        
        # Create test audio data
        test_audio = np.zeros((1000, 1), dtype=np.float32)
        
        # Call audio callback
        recorder.audio_callback(test_audio, 1000, None, None)
        
        # Verify data was added to queue
        queued_data = recorder.audio_queue.get_nowait()
        np.testing.assert_array_equal(queued_data, test_audio)

    def test_process_audio_speech_detection(self):
        """Test audio processing with speech detection."""
        recorder = VADRecorder(self.mock_config, self.mock_obsidian_manager)
        
        # Mock VAD model to detect speech
        self.mock_model.return_value = torch.tensor([0.8])  # Above threshold
        
        # Create test audio data
        test_audio = np.zeros((1000, 1), dtype=np.float32)
        
        # Start processing
        recorder.recording = True
        recorder.audio_queue.put(test_audio)
        
        # Run process_audio in a thread
        process_thread = threading.Thread(target=recorder.process_audio)
        process_thread.start()
        
        # Let it process for a moment
        recorder.stop_event.set()
        process_thread.join(timeout=1)
        
        # Verify model was called with correct input
        self.mock_model.assert_called()

    @patch('pydub.AudioSegment')
    def test_save_recording(self, mock_audio_segment):
        """Test saving a recording."""
        recorder = VADRecorder(self.mock_config, self.mock_obsidian_manager)
        
        # Create test buffer
        test_buffer = [np.zeros((1000, 1), dtype=np.float32)]
        
        # Mock AudioSegment
        mock_segment = MagicMock()
        mock_audio_segment.from_wav.return_value = mock_segment
        
        # Save recording
        recorder.save_recording(test_buffer)
        
        # Verify file was saved and processed
        mock_segment.export.assert_called_once()
        self.mock_obsidian_manager.process_vad_recording.assert_called_once()

if __name__ == '__main__':
    unittest.main()
