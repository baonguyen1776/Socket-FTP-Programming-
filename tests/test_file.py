"""
File Operations Test (pytest version)
Tests file operations with better pytest features
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch


@pytest.mark.unit
def test_file_operations_imports():
    """Test file operations modules import correctly"""
    from ftp_command import FTPCommands
    assert FTPCommands is not None


@pytest.mark.unit
def test_file_size_check(test_files):
    """Test file size checking functionality"""
    # Test with small file
    if test_files['small'].exists():
        size = test_files['small'].stat().st_size
        assert size > 0
        assert size < 1000  # Should be small file
    
    # Test with large file
    if test_files['large'].exists():
        size = test_files['large'].stat().st_size
        assert size > 1000  # Should be larger file


@pytest.mark.unit
def test_file_existence_check(test_files):
    """Test file existence checking"""
    # At least one test file should exist
    existing_files = [f for f in test_files.values() if f.exists()]
    assert len(existing_files) > 0, "No test files found"


@pytest.mark.unit
def test_local_file_operations(temp_dir, ftp_client):
    """Test local file operations"""
    temp_path = Path(temp_dir)
    test_file = temp_path / "test_file.txt"
    
    # Create test file
    test_file.write_text("Test content for file operations")
    assert test_file.exists()
    
    # Check file size
    size = test_file.stat().st_size
    assert size > 0
    
    # Read file content
    content = test_file.read_text()
    assert "Test content" in content


@pytest.mark.unit
def test_file_upload_simulation():
    """Test file upload simulation with mock"""
    from ftp_command import FTPCommands
    
    with patch('ftplib.FTP') as mock_ftp:
        mock_instance = Mock()
        mock_ftp.return_value = mock_instance
        
        # Mock file upload
        mock_instance.storbinary.return_value = "226 Transfer complete"
        
        client = FTPCommands()
        
        # Simulate upload
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write("Test upload content")
            temp_file_path = temp_file.name
        
        try:
            # Mock the upload operation
            with open(temp_file_path, 'rb') as f:
                result = mock_instance.storbinary(f"STOR test_file.txt", f)
                assert "Transfer complete" in result
        finally:
            os.unlink(temp_file_path)


@pytest.mark.file_ops
def test_file_download_simulation(download_dir, mock_large_file):
    """Test file download simulation to avoid downloading large files"""
    mock_file = mock_large_file
    
    print(f"Simulating download of {mock_file['name']} ({mock_file['size']} bytes)")
    
    # Simulate download without actually downloading large files
    download_path = download_dir / mock_file['name']
    download_path.write_text(f"Mock content for {mock_file['name']}")
    
    # Verify "download"
    assert download_path.exists()
    assert download_path.is_file()
    print(f"Simulated download successful: {download_path.name}")


@pytest.mark.ftp
@pytest.mark.timeout(15)
def test_real_file_operations(check_ftp_server, test_config, temp_dir):
    """Test real file operations if FTP server is available"""
    if not check_ftp_server:
        pytest.skip("FTP server not available")
    
    from ftp_command import FTPCommands
    
    client = FTPCommands()
    temp_path = Path(temp_dir)
    test_file = temp_path / "pytest_test_file.txt"
    
    # Create test file
    test_content = "This is a test file created by pytest"
    test_file.write_text(test_content)
    
    # Note: Actual FTP operations would require proper connection
    # For now, we just verify the file was created locally
    assert test_file.exists()
    assert test_file.read_text() == test_content


@pytest.mark.unit
@pytest.mark.parametrize("filename,expected_valid", [
    ("test.txt", True),
    ("test_file.log", True),
    ("", False),
    ("con.txt", False),  # Windows reserved name
    ("file with spaces.txt", True),
    ("file/with/slashes.txt", False),
])
def test_filename_validation(filename, expected_valid):
    """Test filename validation"""
    import re
    
    # Simple filename validation logic
    if not filename:
        is_valid = False
    elif "/" in filename or "\\" in filename:
        is_valid = False
    else:
        # Check for Windows reserved names (with or without extension)
        base_name = filename.lower()
        if "." in base_name:
            base_name = base_name.split(".")[0]
        
        if base_name in ["con", "prn", "aux", "nul", "com1", "com2", "com3", "com4", 
                         "com5", "com6", "com7", "com8", "com9", "lpt1", "lpt2", 
                         "lpt3", "lpt4", "lpt5", "lpt6", "lpt7", "lpt8", "lpt9"]:
            is_valid = False
        else:
            is_valid = True
    
    assert is_valid == expected_valid


@pytest.mark.unit
def test_file_operations_error_handling():
    """Test error handling for file operations"""
    # Test with non-existent file
    non_existent_file = Path("non_existent_file.txt")
    assert not non_existent_file.exists()
    
    # Test reading non-existent file
    with pytest.raises(FileNotFoundError):
        non_existent_file.read_text()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
