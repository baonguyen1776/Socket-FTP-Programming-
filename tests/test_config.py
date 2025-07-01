"""
Test configuration file containing settings for FTP server and ClamAV testing
"""

import os

class TestConfig:
    # FTP Server Configuration  
    FTP_HOST = '127.0.0.1'  # Sync with Client/config.py
    FTP_PORT = 21
    FTP_USERNAME = None  # Will be prompted
    FTP_PASSWORD = None  # Will be prompted
    
    # ClamAV Agent Configuration  
    CLAMAV_HOST = '127.0.0.1'
    CLAMAV_PORT = 9001
    
    # Test Data Configuration
    TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'test_data')
    TEST_RESULTS_FILE = os.path.join(os.path.dirname(__file__), 'test_results.txt')
    
    # Test Files
    SMALL_TEXT_FILE = 'small_test.txt'
    LARGE_TEXT_FILE = 'large_test.txt'
    BINARY_FILE = 'test_image.jpg'
    VIRUS_TEST_FILE = 'eicar_test.txt'  # EICAR test virus file
    
    # Timeout settings
    FTP_TIMEOUT = 30
    CLAMAV_TIMEOUT = 10
    
    @classmethod
    def get_credentials(cls):
        """Get FTP credentials from environment variables only"""
        username = os.getenv('FTP_TEST_USER')
        password = os.getenv('FTP_TEST_PASS')
        
        if not username or not password:
            raise ValueError(
                "Environment variables FTP_TEST_USER and FTP_TEST_PASS must be set.\n"
                "Example:\n"
                "  $env:FTP_TEST_USER=\"your_username\"\n"
                "  $env:FTP_TEST_PASS=\"your_password\""
            )
        
        cls.FTP_USERNAME = username
        cls.FTP_PASSWORD = password
        return username, password
    
    @classmethod
    def get_ftp_config(cls):
        """Get FTP server configuration"""
        host = os.getenv('FTP_TEST_HOST', cls.FTP_HOST)
        port = int(os.getenv('FTP_TEST_PORT', cls.FTP_PORT))
        return host, port
