"""
FTP Client Test Suite Package - Pytest Edition

Modern test suite using pytest with better features:
- Automatic fixtures and setup/teardown
- Timeout protection to prevent hanging
- Marker-based test categorization  
- HTML reporting and better output
- Mock testing for offline development

Usage:
    python test_runner.py           # Interactive menu
    python -m pytest -m unit       # Quick unit tests
    python -m pytest -v            # All tests with verbose output
    python test.py quick           # Shortcut for quick tests
"""

__version__ = "3.0.0-pytest"
__author__ = "FTP Client Test Team"

# Import test configuration for easy access
from .test_config import TestConfig

__all__ = [
    'TestConfig',
    'test_session',
    'test_file', 
    'test_directory',
    'test_local',
    'test_config_validation'
]
