import os
import pytest
import tempfile
import json
from datetime import datetime
from pydub import AudioSegment
from src.audio_processor import AudioProcessor

@pytest.fixture
def sample_wav_file():
    """Create a temporary WAV file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
        # Create a simple sine wave audio
        sine_wave = AudioSegment.silent(duration=1000)  # 1 second of silence
        sine_wave.export(temp_wav.name, format='wav')
        yield temp_wav.name
    # Cleanup
    os.unlink(temp_wav.name)

@pytest.fixture
def mock_config(tmp_path):
    """Create a mock configuration file."""
    config_data = {
        'whisper': {
            'model': 'tiny',
            'language': 'en'
        }
    }
    config_path = tmp_path / 'config.json'
    with open(config_path, 'w') as f:
        json.dump(config_data, f)
    return str(config_path)

def test_audio_processor_initialization(mock_config):
    """Test AudioProcessor initialization with a custom config."""
    processor = AudioProcessor(config_path=mock_config)
    
    assert processor.default_model == 'tiny'
    assert processor.default_language == 'en'
    assert processor.model is not None

def test_convert_to_mp3(sample_wav_file):
    """Test converting WAV to MP3."""
    processor = AudioProcessor()
    creation_time = datetime.now()
    
    mp3_path = processor.convert_to_mp3(sample_wav_file, creation_time)
    
    assert mp3_path is not None
    assert mp3_path.endswith('.mp3')
    assert os.path.exists(mp3_path)
    
    # Cleanup
    os.unlink(mp3_path)

def test_convert_to_mp3_invalid_file():
    """Test conversion with an invalid file."""
    processor = AudioProcessor()
    
    result = processor.convert_to_mp3('/path/to/nonexistent/file.wav')
    
    assert result is None

def test_transcribe_audio(sample_wav_file):
    """Test audio transcription."""
    processor = AudioProcessor()
    
    # Note: This test might fail if the sample audio is too short or not speech
    transcription = processor.transcribe_audio(sample_wav_file)
    
    # Since our sample is just silence, transcription might be empty or None
    assert transcription is not None

def test_transcribe_audio_with_language(sample_wav_file):
    """Test audio transcription with a specific language."""
    processor = AudioProcessor()
    
    transcription = processor.transcribe_audio(sample_wav_file, language='en')
    
    assert transcription is not None

def test_config_file_not_found(tmp_path):
    """Test behavior when config file is not found."""
    non_existent_config = str(tmp_path / 'nonexistent_config.json')
    
    # This should log a warning and use default settings
    processor = AudioProcessor(config_path=non_existent_config)
    
    assert processor.default_model == 'base'
    assert processor.default_language == 'en'
    assert processor.model is not None

def test_config_file_invalid_json(tmp_path):
    """Test behavior with an invalid JSON config file."""
    invalid_config_path = tmp_path / 'invalid_config.json'
    with open(invalid_config_path, 'w') as f:
        f.write('{ invalid json }')
    
    # This should log an error and use default settings
    processor = AudioProcessor(config_path=str(invalid_config_path))
    
    assert processor.default_model == 'base'
    assert processor.default_language == 'en'
    assert processor.model is not None
