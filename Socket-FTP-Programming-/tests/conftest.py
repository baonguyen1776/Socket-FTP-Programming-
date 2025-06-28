import pytest
import os
import sys
import tempfile
from unittest.mock import Mock, MagicMock

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

@pytest.fixture
def mock_ftp_connection():
    """Mock FTP connection object"""
    mock_ftp = MagicMock()
    mock_ftp.connect.return_value = None
    mock_ftp.login.return_value = "230 Login successful"
    mock_ftp.pwd.return_value = "/home/testuser"
    mock_ftp.cwd.return_value = "250 Directory changed"
    mock_ftp.dir.return_value = None
    mock_ftp.quit.return_value = "221 Goodbye"
    mock_ftp.set_pasv.return_value = None
    return mock_ftp

@pytest.fixture
def temp_test_file():
    """Create a temporary test file"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("This is a test file for FTP testing")
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.remove(temp_path)

@pytest.fixture
def mock_virus_scanner():
    """Mock virus scanner that returns clean results"""
    mock_scanner = MagicMock()
    mock_scanner.scan_file.return_value = (True, "Clean")
    return mock_scanner

@pytest.fixture
def mock_clamav_agent_socket():
    """Mock socket for ClamAV agent communication"""
    mock_socket = MagicMock()
    mock_socket.connect.return_value = None
    mock_socket.sendall.return_value = None
    mock_socket.recv.return_value = b"CLEAN"
    return mock_socket
