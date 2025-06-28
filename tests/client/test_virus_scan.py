import pytest
import sys
import os
from unittest.mock import Mock, MagicMock, patch

# Add Client directory to path
client_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'Client')
sys.path.insert(0, client_dir)

from virus_scan import VirusScan


class TestVirusScan:
    """Test cases for VirusScan class"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.virus_scan = VirusScan()
    
    @patch('socket.socket')
    def test_scan_file_clean(self, mock_socket_class, temp_test_file):
        """Test scanning a clean file"""
        # Mock socket instance
        mock_socket = MagicMock()
        mock_socket_class.return_value.__enter__.return_value = mock_socket
        mock_socket.recv.return_value = b"OK              "  # 16 bytes padded
        
        # Test
        is_clean, result = self.virus_scan.scan_file(temp_test_file)
        
        # Assertions
        assert is_clean is True
        assert result == "Good file."
        mock_socket.connect.assert_called_once()
        mock_socket.sendall.assert_called()
    
    def test_scan_file_not_found(self):
        """Test scanning a non-existent file"""
        is_clean, result = self.virus_scan.scan_file("nonexistent_file.txt")
        
        assert is_clean is False
        assert result == "ERROR_FILENOTFOUND"
    
    def test_scan_directory_instead_of_file(self, tmp_path):
        """Test scanning a directory instead of file"""
        is_clean, result = self.virus_scan.scan_file(str(tmp_path))
        
        assert is_clean is False
        assert result == "ERROR_NOTFILE"
    
    @patch('socket.socket')
    def test_scan_file_virus_detected(self, mock_socket_class, temp_test_file):
        """Test scanning a file with virus"""
        # Mock socket instance
        mock_socket = MagicMock()
        mock_socket_class.return_value.__enter__.return_value = mock_socket
        mock_socket.recv.return_value = b"FOUND           "  # 16 bytes padded
        
        # Test
        is_clean, result = self.virus_scan.scan_file(temp_test_file)
        
        # Assertions
        assert is_clean is False
        assert result == "Bad file."
    
    @patch('socket.socket')
    def test_scan_file_connection_error(self, mock_socket_class, temp_test_file):
        """Test connection error to ClamAV agent"""
        # Mock socket to raise connection error
        mock_socket = MagicMock()
        mock_socket_class.return_value.__enter__.return_value = mock_socket
        mock_socket.connect.side_effect = ConnectionRefusedError("Connection refused")
        
        # Test
        is_clean, result = self.virus_scan.scan_file(temp_test_file)
        
        # Assertions
        assert is_clean is False
        assert result == "ERROR_CONNECTION"
    
    @patch('socket.socket')
    def test_scan_file_timeout(self, mock_socket_class, temp_test_file):
        """Test timeout during scanning"""
        # Mock socket to raise timeout
        mock_socket = MagicMock()
        mock_socket_class.return_value.__enter__.return_value = mock_socket
        mock_socket.recv.side_effect = TimeoutError("Operation timed out")
        
        # Test
        is_clean, result = self.virus_scan.scan_file(temp_test_file)
        
        # Assertions
        assert is_clean is False
        assert result == "ERROR_TIMEOUT"
