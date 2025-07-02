"""
Pytest fixtures and configuration for FTP Client tests
"""
import os
import sys
import socket
import tempfile
import shutil
from pathlib import Path
import pytest
from collections import defaultdict

# Add paths for imports
current_dir = Path(__file__).parent
client_dir = current_dir.parent / 'Client'
sys.path.insert(0, str(client_dir))
sys.path.insert(0, str(current_dir))

from test_config import TestConfig


@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration"""
    return TestConfig


@pytest.fixture(scope="function")
def temp_dir():
    """Create temporary directory for tests"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture(scope="function")
def ftp_client():
    """Create FTP client instance"""
    try:
        from ftp_command import FTPCommands
        client = FTPCommands()
        # Tắt prompt trong môi trường test để tránh lỗi stdin capture
        client.prompt_on_mget_mput = False
        yield client
        # Cleanup: disconnect if connected
        try:
            if hasattr(client, 'ftp') and client.ftp:
                client.ftp.quit()
        except:
            pass
    except ImportError:
        pytest.skip("FTPCommands not available")


@pytest.fixture(scope="session")
def check_ftp_server():
    """Check if FTP server is available"""
    try:
        host, port = TestConfig.get_ftp_config()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


@pytest.fixture(scope="session")
def check_clamav_server():
    """Check if ClamAV server is available"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((TestConfig.CLAMAV_HOST, TestConfig.CLAMAV_PORT))
        sock.close()
        return result == 0
    except Exception:
        return False


@pytest.fixture(scope="function")
def mock_large_file():
    """Create mock large file info without actual large file"""
    return {
        'name': 'large_file_simulation.txt',
        'size': 1024 * 1024 * 10,  # 10MB simulation
        'content_sample': 'This would be a large file content...',
        'mock': True
    }


@pytest.fixture(scope="function")
def download_dir():
    """Create and manage downloads directory for tests"""
    downloads_path = Path(__file__).parent / "downloads"
    downloads_path.mkdir(exist_ok=True)
    
    # Store initial files for cleanup decision
    initial_files = set(downloads_path.glob("*"))
    
    yield downloads_path
    
    # Auto cleanup for tests - remove new files created during testing
    new_files = set(downloads_path.glob("*")) - initial_files
    if new_files:
        print(f"\nCleaning up {len(new_files)} test files from downloads/")
        for file in new_files:
            try:
                file.unlink()
                print(f"Deleted: {file.name}")
            except Exception as e:
                print(f"Could not delete {file.name}: {e}")


@pytest.fixture(scope="session") 
def ftp_credentials():
    """Get FTP credentials for testing - use env vars or defaults"""
    # Try environment variables first
    username = os.getenv('FTP_TEST_USER')
    password = os.getenv('FTP_TEST_PASS')
    
    # Use defaults if not set (for automated testing)
    if not username:
        username = 'ftpuser'  # Default for test environment
    if not password:
        password = '12345'    # Default for test environment
        
    return username, password


@pytest.fixture(scope="session")
def interactive_credentials():
    """Get credentials with prompts for interactive testing"""
    return TestConfig.get_credentials()


@pytest.fixture(scope="session")
def interactive_cleanup():
    """Ask user about cleanup when running interactively"""
    def cleanup_prompt():
        try:
            cleanup = input("Delete test files after completion? (y/N): ").strip().lower()
            return cleanup in ['y', 'yes']
        except:
            return False  # Default to no cleanup if input fails
    return cleanup_prompt


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment before each test"""
    # Store original working directory
    original_cwd = os.getcwd()
    
    yield
    
    # Restore original working directory
    os.chdir(original_cwd)


def pytest_configure(config):
    """Configure pytest"""
    # Add custom markers
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow tests")
    config.addinivalue_line("markers", "ftp: FTP server required")
    config.addinivalue_line("markers", "clamav: ClamAV server required")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically"""
    for item in items:
        # Add unit marker to tests that don't require external services
        if "ftp" not in item.keywords and "clamav" not in item.keywords:
            item.add_marker(pytest.mark.unit)
        
        # Add integration marker to tests requiring external services
        if "ftp" in item.keywords or "clamav" in item.keywords:
            item.add_marker(pytest.mark.integration)


def pytest_runtest_setup(item):
    """Setup before running each test"""
    # Skip FTP tests if server not available
    if "ftp" in item.keywords:
        if not check_ftp_server_available():
            pytest.skip("FTP server not available")
    
    # Skip ClamAV tests if server not available
    if "clamav" in item.keywords:
        if not check_clamav_server_available():
            pytest.skip("ClamAV server not available")
    
    # Skip integration tests if credentials not set
    if "integration" in item.keywords:
        if not check_credentials_available():
            pytest.skip("FTP credentials not set. Set FTP_TEST_USER and FTP_TEST_PASS environment variables")


def check_credentials_available():
    """Check if FTP credentials are available and valid"""
    import os
    username = os.getenv('FTP_TEST_USER')
    password = os.getenv('FTP_TEST_PASS')
    
    # Check if credentials exist
    if not username or not password:
        return False
    
    # Check if credentials are not just dummy values
    if username.lower() in ['test', 'user', 'admin', 'ftp'] and len(username) < 5:
        return False
    
    if password.lower() in ['test', 'pass', 'password', '123'] and len(password) < 5:
        return False
    
    return True


def check_ftp_server_available():
    """Quick check if FTP server is available"""
    try:
        host, port = TestConfig.get_ftp_config()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False


def check_clamav_server_available():
    """Quick check if ClamAV server is available"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((TestConfig.CLAMAV_HOST, TestConfig.CLAMAV_PORT))
        sock.close()
        return result == 0
    except:
        return False


@pytest.fixture(scope="function")
def ftp_cleanup_tracker():
    """Track and cleanup files/directories created on FTP server during tests"""
    class FTPCleanupTracker:
        def __init__(self):
            self.files_to_delete = []
            self.dirs_to_delete = []
        
        def add_file(self, path):
            """Add a file path to be cleaned up after the test"""
            self.files_to_delete.append(path)
            
        def add_directory(self, path):
            """Add a directory path to be cleaned up after the test"""
            self.dirs_to_delete.append(path)
            
        def cleanup(self, ftp_client):
            """Clean up all tracked files and directories"""
            if not hasattr(ftp_client, 'ftp') or ftp_client.ftp is None:
                return
                
            # Remember original directory
            try:
                original_dir = ftp_client.ftp.pwd()
            except:
                original_dir = "/"
                
            # Delete files first
            failed_files = []
            for file_path in self.files_to_delete:
                try:
                    ftp_client.do_delete(file_path)
                    print(f"Deleted remote file: {file_path}")
                except Exception as e:
                    failed_files.append((file_path, str(e)))
            
            # Then delete directories (in reverse order to handle nested dirs)
            failed_dirs = []
            for dir_path in reversed(self.dirs_to_delete):
                try:
                    # Ensure we're not in the directory we're trying to delete
                    ftp_client.do_cd("/")
                    
                    # Check if directory has files and delete them first
                    try:
                        ftp_client.do_cd(dir_path)
                        files = ftp_client.ftp.nlst()
                        for file in files:
                            if file not in ['.', '..']:
                                try:
                                    ftp_client.do_delete(file)
                                except:
                                    pass
                        ftp_client.do_cd("/")
                    except:
                        pass
                    
                    ftp_client.do_rmdir(dir_path)
                    print(f"Deleted remote directory: {dir_path}")
                except Exception as e:
                    failed_dirs.append((dir_path, str(e)))
            
            # Report failures
            if failed_files or failed_dirs:
                print("\nWARNING: Some FTP cleanup operations failed:")
                for path, err in failed_files:
                    print(f"- Could not delete file {path}: {err}")
                for path, err in failed_dirs:
                    print(f"- Could not delete directory {path}: {err}")
            
            # Return to original directory
            try:
                ftp_client.do_cd(original_dir)
            except:
                pass
    
    tracker = FTPCleanupTracker()
    yield tracker


@pytest.fixture(scope="function")
def ftp_client_with_cleanup(ftp_client, ftp_cleanup_tracker):
    """Create FTP client instance with automatic cleanup of remote files"""
    # Tắt prompt trong môi trường test để tránh lỗi stdin capture
    original_prompt_setting = ftp_client.prompt_on_mget_mput
    ftp_client.prompt_on_mget_mput = False
    
    try:
        yield ftp_client, ftp_cleanup_tracker
    finally:
        # Khôi phục setting ban đầu
        ftp_client.prompt_on_mget_mput = original_prompt_setting
        # Cleanup tracked FTP resources
        ftp_cleanup_tracker.cleanup(ftp_client)
