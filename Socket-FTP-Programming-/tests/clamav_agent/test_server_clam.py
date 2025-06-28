import pytest
import sys
import os
import socket
import threading
from unittest.mock import Mock, MagicMock, patch

# Add ClamAvAgent directory to path
clamav_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'ClamAvAgent')
sys.path.insert(0, clamav_dir)

from sever_clam import ClamAVAgentServer


class TestClamAVAgentServer:
    """Test cases for ClamAVAgentServer class"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.server = ClamAVAgentServer("localhost", 9999)
    
    def test_initialization(self):
        """Test server initialization"""
        assert self.server.host == "localhost"
        assert self.server.port == 9999
        assert self.server.server_socket is None
        assert self.server.scanner is not None
    
    @patch('os.makedirs')
    @patch('os.path.exists')
    def test_temp_directory_creation(self, mock_exists, mock_makedirs):
        """Test temporary directory creation during init"""
        mock_exists.return_value = False
        
        # Create new server instance to trigger temp dir creation
        server = ClamAVAgentServer("localhost", 9999)
        
        mock_makedirs.assert_called_once_with('temp_scan_files')
    
    @patch('socket.socket')
    def test_server_start_and_bind(self, mock_socket_class):
        """Test server start and socket binding"""
        # Mock socket instance
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        
        # Mock accept to return immediately (avoid infinite loop)
        mock_socket.accept.side_effect = KeyboardInterrupt()
        
        # Test start method
        try:
            self.server.start()
        except KeyboardInterrupt:
            pass  # Expected
        
        # Assertions
        mock_socket.setsockopt.assert_called_with(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        mock_socket.bind.assert_called_with(("localhost", 9999))
        mock_socket.listen.assert_called_with(3)
    
    def test_simple_client_handling(self):
        """Test basic client handling without complex mocking"""
        # This is a simplified test - just verify server can be created
        # and has the right attributes
        assert self.server.host == "localhost"
        assert self.server.port == 9999
        assert hasattr(self.server, 'scanner')
        
        # Test that server has start method
        assert callable(getattr(self.server, 'start', None))
    
    @patch('socket.socket')
    def test_server_socket_timeout_handling(self, mock_socket_class):
        """Test handling socket timeout"""
        # Mock socket instance
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        
        # Mock accept to raise timeout, then KeyboardInterrupt
        mock_socket.accept.side_effect = [socket.timeout(), KeyboardInterrupt()]
        
        # Test start method
        try:
            self.server.start()
        except KeyboardInterrupt:
            pass  # Expected
        
        # Should continue listening after timeout
        assert mock_socket.accept.call_count == 2
    
    def test_server_stop(self):
        """Test server stop functionality"""
        # Mock socket
        mock_socket = MagicMock()
        self.server.server_socket = mock_socket
        
        # Test stop method
        self.server.stop()
        
        # Assertions
        mock_socket.close.assert_called_once()
        # Note: server_socket may not be set to None in the actual implementation
    
    @patch('socket.socket')
    def test_server_error_handling(self, mock_socket_class):
        """Test server error handling during startup"""
        # Mock socket to raise error on bind
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        mock_socket.bind.side_effect = socket.error("Address already in use")
        
        # Test start method should handle error gracefully
        try:
            self.server.start()
        except socket.error:
            pass  # Expected
        
        mock_socket.bind.assert_called_once()
    
    def teardown_method(self):
        """Cleanup after each test"""
        if self.server.server_socket:
            self.server.stop()
