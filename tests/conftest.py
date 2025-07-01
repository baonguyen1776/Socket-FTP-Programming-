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
def test_files():
    """Provide test files with size info"""
    test_data_dir = Path(__file__).parent / "test_data"
    
    files = {
        'small': test_data_dir / "small_test.txt",
        'large': test_data_dir / "large_test.txt", 
        'virus': test_data_dir / "eicar_test.txt",
        'virus_safe': test_data_dir / "eicar_safe.txt"
    }
    
    # Create small test file if not exists
    if not files['small'].exists():
        files['small'].write_text("Small test file content for FTP testing.")
    
    # Create moderate "large" file if not exists (not actually large to avoid issues)
    if not files['large'].exists():
        content = "Large test file content.\n" * 100  # Just 2-3KB, not truly large
        files['large'].write_text(content)
    
    return files


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
    
    # Ensure test data directory exists
    os.makedirs(TestConfig.TEST_DATA_DIR, exist_ok=True)
    
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
