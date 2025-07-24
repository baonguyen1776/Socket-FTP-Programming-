"""
Fixtures và cấu hình Pytest cho FTP Client tests
"""
import os
import sys
import socket
import tempfile
import shutil
from pathlib import Path
import pytest
from collections import defaultdict

# Thêm đường dẫn cho imports
current_dir = Path(__file__).parent
client_dir = current_dir.parent / 'Client'
sys.path.insert(0, str(client_dir))
sys.path.insert(0, str(current_dir))

from test_config import TestConfig


@pytest.fixture(scope="session")
def test_config():
    """Cung cấp cấu hình test"""
    return TestConfig


@pytest.fixture(scope="function")
def temp_dir():
    """Tạo thư mục tạm thời cho tests"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture(scope="function")
def ftp_client():
    """Tạo instance FTP client"""
    try:
        from ftp_command import FTPCommands
        client = FTPCommands()
        # Tắt prompt trong môi trường test để tránh lỗi stdin capture
        client.prompt_on_mget_mput = False
        yield client
        # Cleanup: ngắt kết nối nếu đang kết nối
        try:
            if hasattr(client, 'ftp') and client.ftp:
                client.ftp.quit()
        except:
            pass
    except ImportError:
        pytest.skip("FTPCommands not available")


@pytest.fixture(scope="session")
def check_ftp_server():
    """Kiểm tra nếu FTP server có sẵn"""
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
    """Kiểm tra nếu ClamAV server có sẵn"""
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
    """Tạo thông tin file lớn giả lập mà không có file lớn thực tế"""
    return {
        'name': 'large_file_simulation.txt',
        'size': 1024 * 1024 * 10,  # Giả lập 10MB
        'content_sample': 'This would be a large file content...',
        'mock': True
    }


@pytest.fixture(scope="function")
def download_dir():
    """Tạo và quản lý thư mục downloads cho tests"""
    downloads_path = Path(__file__).parent / "downloads"
    downloads_path.mkdir(exist_ok=True)
    
    # Lưu các file ban đầu để quyết định cleanup
    initial_files = set(downloads_path.glob("*"))
    
    yield downloads_path
    
    # Tự động cleanup cho tests - xóa file mới được tạo trong quá trình testing
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
    """Lấy thông tin đăng nhập FTP cho testing - sử dụng env vars hoặc mặc định"""
    # Thử biến môi trường trước
    username = os.getenv('FTP_TEST_USER')
    password = os.getenv('FTP_TEST_PASS')
    
    # Sử dụng mặc định nếu không được set (cho automated testing)
    if not username:
        username = 'None'  # Mặc định cho môi trường test
    if not password:
        password = 'None'    # Mặc định cho môi trường test
        
    return username, password


@pytest.fixture(scope="session")
def interactive_credentials():
    """Lấy thông tin đăng nhập với prompts cho interactive testing"""
    return TestConfig.get_credentials()


@pytest.fixture(scope="session")
def interactive_cleanup():
    """Hỏi user về cleanup khi chạy tương tác"""
    def cleanup_prompt():
        try:
            cleanup = input("Xóa file test sau khi hoàn thành? (y/N): ").strip().lower()
            return cleanup in ['y', 'yes']
        except:
            return False  # Mặc định không cleanup nếu input thất bại
    return cleanup_prompt


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Thiết lập môi trường test trước mỗi test"""
    # Lưu thư mục làm việc ban đầu
    original_cwd = os.getcwd()
    
    yield
    
    # Khôi phục thư mục làm việc ban đầu
    os.chdir(original_cwd)


def pytest_configure(config):
    """Cấu hình pytest"""
    # Thêm custom markers
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow tests")
    config.addinivalue_line("markers", "ftp: Yêu cầu FTP server")
    config.addinivalue_line("markers", "clamav: Yêu cầu ClamAV server")


def pytest_collection_modifyitems(config, items):
    """Chỉnh sửa thu thập test để thêm markers tự động"""
    for item in items:
        # Thêm unit marker cho tests không yêu cầu external services
        if "ftp" not in item.keywords and "clamav" not in item.keywords:
            item.add_marker(pytest.mark.unit)
        
        # Thêm integration marker cho tests yêu cầu external services
        if "ftp" in item.keywords or "clamav" in item.keywords:
            item.add_marker(pytest.mark.integration)


def pytest_runtest_setup(item):
    """Thiết lập trước khi chạy mỗi test"""
    # Bỏ qua FTP tests nếu server không có sẵn
    if "ftp" in item.keywords:
        if not check_ftp_server_available():
            pytest.skip("FTP server không có sẵn")
    
    # Bỏ qua ClamAV tests nếu server không có sẵn
    if "clamav" in item.keywords:
        if not check_clamav_server_available():
            pytest.skip("ClamAV server không có sẵn")
    
    # Bỏ qua integration tests nếu thông tin đăng nhập không được set
    if "integration" in item.keywords:
        if not check_credentials_available():
            pytest.skip("Thông tin đăng nhập FTP chưa được đặt. Đặt biến môi trường FTP_TEST_USER và FTP_TEST_PASS")


def check_credentials_available():
    """Kiểm tra nếu thông tin đăng nhập FTP có sẵn và hợp lệ"""
    import os
    username = os.getenv('FTP_TEST_USER')
    password = os.getenv('FTP_TEST_PASS')
    
    # Kiểm tra nếu thông tin đăng nhập tồn tại
    if not username or not password:
        return False
    
    # Kiểm tra nếu thông tin đăng nhập không chỉ là giá trị dummy
    if username.lower() in ['test', 'user', 'admin', 'ftp'] and len(username) < 5:
        return False
    
    if password.lower() in ['test', 'pass', 'password', '123'] and len(password) < 5:
        return False
    
    return True


def check_ftp_server_available():
    """Kiểm tra nhanh nếu FTP server có sẵn"""
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
    """Kiểm tra nhanh nếu ClamAV server có sẵn"""
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
    """Theo dõi và dọn dẹp files/directories được tạo trên FTP server trong quá trình tests"""
    class FTPCleanupTracker:
        def __init__(self):
            self.files_to_delete = []
            self.dirs_to_delete = []
        
        def add_file(self, path):
            """Thêm đường dẫn file để được dọn dẹp sau test"""
            self.files_to_delete.append(path)
            
        def add_directory(self, path):
            """Thêm đường dẫn thư mục để được dọn dẹp sau test"""
            self.dirs_to_delete.append(path)
            
        def cleanup(self, ftp_client):
            """Dọn dẹp tất cả files và directories được theo dõi"""
            if not hasattr(ftp_client, 'ftp') or ftp_client.ftp is None:
                return
                
            # Nhớ thư mục ban đầu
            try:
                original_dir = ftp_client.ftp.pwd()
            except:
                original_dir = "/"
                
            # Xóa files trước
            failed_files = []
            for file_path in self.files_to_delete:
                try:
                    ftp_client.do_delete(file_path)
                    print(f"Đã xóa file remote: {file_path}")
                except Exception as e:
                    failed_files.append((file_path, str(e)))
            
            # Sau đó xóa directories (theo thứ tự ngược để xử lý nested dirs)
            failed_dirs = []
            for dir_path in reversed(self.dirs_to_delete):
                try:
                    # Đảm bảo chúng ta không ở trong thư mục đang cố xóa
                    ftp_client.do_cd("/")
                    
                    # Kiểm tra nếu thư mục có files và xóa chúng trước
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
                    print(f"Đã xóa thư mục remote: {dir_path}")
                except Exception as e:
                    failed_dirs.append((dir_path, str(e)))
            
            # Báo cáo thất bại
            if failed_files or failed_dirs:
                print("\nCẢNH BÁO: Một số thao tác cleanup FTP thất bại:")
                for path, err in failed_files:
                    print(f"- Không thể xóa file {path}: {err}")
                for path, err in failed_dirs:
                    print(f"- Không thể xóa thư mục {path}: {err}")
            
            # Quay về thư mục ban đầu
            try:
                ftp_client.do_cd(original_dir)
            except:
                pass
    
    tracker = FTPCleanupTracker()
    yield tracker


@pytest.fixture(scope="function")
def ftp_client_with_cleanup(ftp_client, ftp_cleanup_tracker):
    """Tạo instance FTP client với tự động cleanup các file remote"""
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
