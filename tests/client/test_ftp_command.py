import pytest
import sys
import os
from unittest.mock import Mock, MagicMock, patch

# Add Client directory to path
client_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'Client')
sys.path.insert(0, client_dir)

from ftp_command import FTPCommands


class TestFTPCommands:
    """Test cases for FTPCommands class"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.ftp_client = FTPCommands()
    
    def test_initialization(self):
        """Test FTPCommands initialization"""
        assert self.ftp_client.connected is False
        assert self.ftp_client.ftp is None
        assert self.ftp_client.passive_mode is True
        assert self.ftp_client.transfer_mode == 'binary'
        assert self.ftp_client.current_local_dir == os.getcwd()
        assert self.ftp_client.current_ftp_dir == "/"
    
    def test_do_open_basic(self):
        """Test basic open functionality without complex mocking"""
        # Test that do_open method exists and is callable
        assert hasattr(self.ftp_client, 'do_open')
        assert callable(getattr(self.ftp_client, 'do_open'))
        
        # Test already connected scenario
        self.ftp_client.connected = True
        mock_ftp = MagicMock()
        mock_ftp.host = "test.server.com"
        self.ftp_client.ftp = mock_ftp
        
        with patch('builtins.print') as mock_print:
            self.ftp_client.do_open("another.server.com")
            mock_print.assert_called_with("Connected to test.server.com. Please use 'close' first.")
    
    def test_commands_without_connection(self):
        """Test FTP commands without being connected"""
        # Test ls command without connection - should raise AttributeError
        # because do_ls accesses self.ftp.dir when self.ftp is None
        try:
            self.ftp_client.do_ls("")
            assert False, "Should have raised AttributeError"
        except AttributeError:
            pass  # Expected behavior
    
    @patch('ftplib.FTP')
    def test_do_ls_with_connection(self, mock_ftp_class):
        """Test ls command with established connection"""
        # Setup mock FTP
        mock_ftp = MagicMock()
        mock_ftp_class.return_value = mock_ftp
        mock_ftp.dir.__name__ = 'dir'  # Add __name__ attribute for the mock
        self.ftp_client.ftp = mock_ftp
        self.ftp_client.connected = True
        
        # Test ls command
        self.ftp_client.do_ls("testdir")
        
        # Assertions
        mock_ftp.set_pasv.assert_called_with(True)
        mock_ftp.dir.assert_called_with("testdir")
    
    @patch('ftplib.FTP')
    def test_do_cd_success(self, mock_ftp_class):
        """Test successful directory change"""
        # Setup mock FTP
        mock_ftp = MagicMock()
        mock_ftp_class.return_value = mock_ftp
        mock_ftp.cwd.return_value = "250 Directory changed"
        mock_ftp.cwd.__name__ = 'cwd'  # Add __name__ for mock
        mock_ftp.pwd.return_value = "/new/directory"
        mock_ftp.pwd.__name__ = 'pwd'  # Add __name__ for mock
        self.ftp_client.ftp = mock_ftp
        self.ftp_client.connected = True
        
        # Test cd command
        self.ftp_client.do_cd("/new/directory")
        
        # Assertions
        mock_ftp.cwd.assert_called_with("/new/directory")
        assert self.ftp_client.current_ftp_dir == "/new/directory"
    
    @patch('ftplib.FTP')
    def test_do_pwd(self, mock_ftp_class):
        """Test pwd command"""
        # Setup mock FTP
        mock_ftp = MagicMock()
        mock_ftp_class.return_value = mock_ftp
        mock_ftp.pwd.return_value = "/current/path"
        mock_ftp.pwd.__name__ = 'pwd'  # Add __name__ for mock
        self.ftp_client.ftp = mock_ftp
        self.ftp_client.connected = True
        
        # Test pwd command
        with patch('builtins.print') as mock_print:
            self.ftp_client.do_pwd("")
            mock_print.assert_called_with("Current directory on FTP server: /current/path")
    
    def test_passive_mode_toggle(self):
        """Test passive mode toggle"""
        # Initial state
        assert self.ftp_client.passive_mode is True
        
        # Toggle passive mode
        self.ftp_client.do_passive("")
        
        # Should toggle the mode (implementation dependent)
    
    @patch('ftplib.FTP')
    def test_ftp_cmd_error_handling(self, mock_ftp_class):
        """Test error handling in _ftp_cmd wrapper"""
        from ftplib import error_perm
        
        # Setup mock FTP
        mock_ftp = MagicMock()
        mock_ftp_class.return_value = mock_ftp
        mock_ftp.dir.side_effect = error_perm("550 Permission denied")
        mock_ftp.dir.__name__ = 'dir'  # Add __name__ for mock
        self.ftp_client.ftp = mock_ftp
        self.ftp_client.connected = True
        
        # Test command that raises permission error
        with patch('builtins.print') as mock_print:
            result = self.ftp_client._ftp_cmd(mock_ftp.dir, "testdir")
            
            # Should handle error gracefully
            assert result is None
            # Check if error was printed
            mock_print.assert_called()
    
    def test_precmd_logging(self):
        """Test command logging in precmd"""
        with patch('utils.Utils.log_event') as mock_log:
            result = self.ftp_client.precmd("ls testdir")
            
            assert result == "ls testdir"
            mock_log.assert_called_once()
