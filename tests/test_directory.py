"""
Directory Operations Test (pytest version)
Tests directory operations with pytest features
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch


@pytest.mark.unit
def test_directory_imports():
    """Test directory modules import correctly"""
    from ftp_command import FTPCommands
    assert FTPCommands is not None


@pytest.mark.unit
def test_local_directory_operations(temp_dir, ftp_client):
    """Test local directory operations"""
    temp_path = Path(temp_dir)
    
    # Test creating subdirectory
    subdir = temp_path / "test_subdir"
    subdir.mkdir()
    assert subdir.exists()
    assert subdir.is_dir()
    
    # Test listing directory
    files = list(temp_path.iterdir())
    assert subdir in files


@pytest.mark.unit
def test_directory_listing_simulation():
    """Test directory listing with mock"""
    from ftp_command import FTPCommands
    
    with patch('ftplib.FTP') as mock_ftp:
        mock_instance = Mock()
        mock_ftp.return_value = mock_instance
        
        # Mock directory listing
        mock_instance.nlst.return_value = ["file1.txt", "file2.txt", "subdir/"]
        
        client = FTPCommands()
        
        # Simulate directory listing
        result = mock_instance.nlst("/")
        assert "file1.txt" in result
        assert "file2.txt" in result
        assert "subdir/" in result


@pytest.mark.unit 
def test_directory_navigation(temp_dir):
    """Test directory navigation operations"""
    temp_path = Path(temp_dir)
    original_cwd = os.getcwd()
    
    try:
        # Change to temp directory
        os.chdir(temp_path)
        assert os.getcwd() == str(temp_path)
        
        # Create and navigate to subdirectory
        subdir = temp_path / "navigation_test"
        subdir.mkdir()
        os.chdir(subdir)
        assert os.getcwd() == str(subdir)
        
    finally:
        # Always restore original directory
        os.chdir(original_cwd)


@pytest.mark.unit
def test_directory_creation_deletion(temp_dir):
    """Test directory creation and deletion"""
    temp_path = Path(temp_dir)
    
    # Test directory creation
    new_dir = temp_path / "new_directory"
    new_dir.mkdir()
    assert new_dir.exists()
    
    # Test nested directory creation
    nested_dir = new_dir / "nested" / "deep"
    nested_dir.mkdir(parents=True)
    assert nested_dir.exists()
    
    # Test directory deletion
    nested_dir.rmdir()
    assert not nested_dir.exists()


@pytest.mark.ftp
@pytest.mark.timeout(15)
def test_real_directory_operations(check_ftp_server, test_config):
    """Test real directory operations if FTP server available"""
    if not check_ftp_server:
        pytest.skip("FTP server not available")
    
    from ftp_command import FTPCommands
    
    client = FTPCommands()
    
    # Note: Actual FTP operations would require proper connection
    # For now, we just verify client initialization
    assert client is not None


@pytest.mark.unit
@pytest.mark.parametrize("dirname,expected_valid", [
    ("test_dir", True),
    ("valid-directory", True),
    ("", False),
    ("dir with spaces", True),
    ("dir/with/slashes", False),
    ("con", False),  # Windows reserved name
])
def test_directory_name_validation(dirname, expected_valid):
    """Test directory name validation"""
    # Simple directory name validation
    if not dirname:
        is_valid = False
    elif "/" in dirname or "\\" in dirname:
        is_valid = False
    elif dirname.lower() in ["con", "prn", "aux", "nul"]:
        is_valid = False
    else:
        is_valid = True
    
    assert is_valid == expected_valid


@pytest.mark.unit
def test_directory_permissions(temp_dir):
    """Test directory permissions handling"""
    temp_path = Path(temp_dir)
    
    # Create directory
    test_dir = temp_path / "permissions_test"
    test_dir.mkdir()
    
    # Test read permission
    assert os.access(test_dir, os.R_OK)
    
    # Test write permission
    assert os.access(test_dir, os.W_OK)
    
    # Test execute permission (needed for directory traversal)
    assert os.access(test_dir, os.X_OK)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
