import pytest
import sys
import os
import tempfile
from unittest.mock import Mock, MagicMock, patch

# Add ClamAvAgent directory to path
clamav_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'ClamAvAgent')
sys.path.insert(0, clamav_dir)

from scanner import ClamAVScanner


class TestClamAVScanner:
    """Test cases for ClamAVScanner class"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.scanner = ClamAVScanner()
    
    def test_initialization(self):
        """Test scanner initialization"""
        assert self.scanner is not None
    
    @patch('subprocess.Popen')
    def test_scan_clean_file(self, mock_popen):
        """Test scanning a clean file"""
        # Mock subprocess to return clean result
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (b"test_file.txt: OK", b"")
        mock_popen.return_value = mock_process
        
        # Create temporary test file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("Clean test content")
            test_file = f.name
        
        try:
            # Test scan
            result = self.scanner.scan_file(test_file)
            
            # Assertions
            assert result == "OK"
            mock_popen.assert_called_once()
        finally:
            # Cleanup
            if os.path.exists(test_file):
                os.remove(test_file)
    
    @patch('subprocess.Popen')
    def test_scan_infected_file(self, mock_popen):
        """Test scanning an infected file"""
        # Mock subprocess to return virus detection
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.communicate.return_value = (b"test_file.txt: FOUND Win.Test.EICAR_HDB-1", b"")
        mock_popen.return_value = mock_process
        
        # Create temporary test file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*")
            test_file = f.name
        
        try:
            # Test scan
            result = self.scanner.scan_file(test_file)
            
            # Assertions
            assert result == "INFECTED"
            mock_popen.assert_called_once()
        finally:
            # Cleanup
            if os.path.exists(test_file):
                os.remove(test_file)
    
    def test_scan_nonexistent_file(self):
        """Test scanning a file that doesn't exist"""
        result = self.scanner.scan_file("nonexistent_file_12345.txt")
        
        # Should return specific error for file not found
        assert result == "ERROR_FILE_NOT_FOUND"
    
    @patch('subprocess.Popen')
    def test_scan_scanner_error(self, mock_popen):
        """Test handling scanner errors"""
        # Mock subprocess to raise FileNotFoundError (clamscan not found)
        mock_popen.side_effect = FileNotFoundError("clamscan command not found")
        
        # Create temporary test file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("Test content")
            test_file = f.name
        
        try:
            # Test scan
            result = self.scanner.scan_file(test_file)
            
            # Should handle error gracefully
            assert result == "CLAMAV_NOT_FOUND"
        finally:
            # Cleanup
            if os.path.exists(test_file):
                os.remove(test_file)
    
    @patch('subprocess.Popen')
    def test_scan_timeout(self, mock_popen):
        """Test scan timeout handling"""
        # Mock subprocess to raise timeout
        mock_popen.side_effect = Exception("Scan operation timed out")
        
        # Create temporary test file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("Test content")
            test_file = f.name
        
        try:
            # Test scan
            result = self.scanner.scan_file(test_file)
            
            # Should handle timeout gracefully
            assert result.startswith("UNKNOWN_SCAN_ERROR:")
        finally:
            # Cleanup
            if os.path.exists(test_file):
                os.remove(test_file)
    
    def test_scan_large_file(self):
        """Test scanning large files"""
        # Create a larger temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            # Write 1MB of data
            f.write("A" * (1024 * 1024))
            large_file = f.name
        
        try:
            with patch('subprocess.Popen') as mock_popen:
                mock_process = MagicMock()
                mock_process.returncode = 0
                mock_process.communicate.return_value = (f"{large_file}: OK".encode(), b"")
                mock_popen.return_value = mock_process
                
                # Test scan
                result = self.scanner.scan_file(large_file)
                
                # Should handle large files
                assert result == "OK"
        finally:
            # Cleanup
            if os.path.exists(large_file):
                os.remove(large_file)
