"""
FTP Client Test Suite Package - Cleaned Version

This package contains working tests for the FTP client application.
All hanging and problematic tests have been removed and replaced with 
reliable quick tests.

Usage:
    Run test_runner.py for interactive testing menu
    Or run individual test_*_quick.py tests for specific functionality
"""

__version__ = "2.0.0"
__author__ = "FTP Client Test Team"

# Import test configuration for easy access
from .test_config import TestConfig

__all__ = [
    'TestConfig',
    'test_session_quick',
    'test_local_quick', 
    'test_directory_quick',
    'test_file_quick',
    'test_config_validation',
    'test_suite_summary'
]
