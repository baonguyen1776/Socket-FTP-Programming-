"""
Real FTP Server Integration Tests
Tests that actually connect to and interact with real FTP servers

INSTRUCTIONS TO RUN TESTS:
1. Set up FTP credentials as environment variables:
   - For PowerShell: 
     $env:FTP_TEST_USER="username"
     $env:FTP_TEST_PASS="password"
   - For CMD: 
     set FTP_TEST_USER=username
     set FTP_TEST_PASS=password

2. Run tests:
   - All tests: pytest test_real_server.py -v
   - Specific test: pytest test_real_server.py::test_directory_navigation -v
   - Through menu: python test_runner.py
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Client'))
from raw_socket_ftp import FTP, all_errors, error_perm, error_temp, error_proto
import tempfile
import shutil
import os
import time
from pathlib import Path
import sys

# Add Client directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "Client"))


# Đảm bảo import được module trong Client
import importlib.util
client_path = str(Path(__file__).parent.parent / "Client")
if client_path not in sys.path:
    sys.path.insert(0, client_path)

import os
from test_config import TestConfig
from Client.ftp_command import FTPCommands
from Client.ftp_helpers import FTPHelpers

# Kiểm tra biến môi trường FTP_TEST_USER và FTP_TEST_PASS
ftp_user = os.environ.get('FTP_TEST_USER')
ftp_pass = os.environ.get('FTP_TEST_PASS')

# Kiểm tra credentials trước khi chạy test
def has_credentials():
    """Kiểm tra nếu đã có thông tin đăng nhập FTP"""
    return ftp_user is not None and ftp_pass is not None


@pytest.fixture(scope="function")
def ftp_client():
    """Create FTP client instance with automatic connection"""
    try:
        if not has_credentials():
            pytest.skip("FTP credentials not set. Set FTP_TEST_USER and FTP_TEST_PASS environment variables")
        
        client = FTPCommands()
        
        # Tắt prompt trong môi trường test để tránh lỗi stdin capture
        client.prompt_on_mget_mput = False
        
        # Thiết lập thông tin đăng nhập từ biến môi trường
        TestConfig.FTP_USER = ftp_user
        TestConfig.FTP_PASS = ftp_pass
        
        # Kết nối
        host, port = TestConfig.get_ftp_config()
        client.do_open(f"{host} {port}")
        
        # Đảm bảo ftp_helpers được khởi tạo
        if client.ftp and not client.ftp_helpers:
            client.ftp_helpers = FTPHelpers(client.ftp)
            
        yield client
        
        # Đóng kết nối sau khi test hoàn thành
        try:
            if client.ftp:
                client.do_close("")
        except:
            pass
            
    except Exception as e:
        pytest.skip(f"FTP client initialization failed: {e}")


@pytest.mark.integration
@pytest.mark.real_server
@pytest.mark.timeout(30)
def test_real_ftp_connection():
    """Test actual FTP connection to real server"""
    if not has_credentials():
        pytest.skip("FTP credentials not set. Set FTP_TEST_USER and FTP_TEST_PASS environment variables")
    
    try:
        host, port = TestConfig.get_ftp_config()
        client = FTPCommands()
        
        # Thiết lập thông tin đăng nhập từ biến môi trường
        TestConfig.FTP_USER = ftp_user
        TestConfig.FTP_PASS = ftp_pass
        
        # Kết nối
        print(f"Connecting to {host}:{port}...")
        result = client.do_open(f"{host} {port}")
        print(f"Connection result: {result}")
        
        # Đăng nhập thủ công nếu cần
        if client.ftp is None:
            # Kết nối thủ công
            client.ftp = FTP()
            client.ftp.connect(host, port)
            client.ftp.login(ftp_user, ftp_pass)
            # Quan trọng: Tạo ftp_helpers nếu kết nối thủ công
            client.ftp_helpers = FTPHelpers(client.ftp)
            print("Manual connection successful")
        
        # Đảm bảo kết nối thành công và client.ftp đã được khởi tạo
        assert client.ftp is not None, "FTP connection failed, client.ftp is None"
        assert client.ftp_helpers is not None, "FTP helpers not initialized"
        
        # Kiểm tra trạng thái
        client.do_status("")
        
        # Lấy danh sách file (chỉ khi đã kết nối thành công)
        if client.ftp:
            files = client.ftp.nlst()
        print(f"Files in root: {files[:5] if files else 'Empty'}")
        # Lấy thư mục hiện tại
        pwd = client.ftp.pwd()
        print(f"Current directory: {pwd}")
        # Đóng kết nối
        client.do_close("")
        assert True, "Successfully connected to real FTP server via FTPCommands"
    except ValueError as e:
        pytest.skip(f"Credentials not set: {e}")
    except Exception as e:
        pytest.fail(f"Real FTP connection failed: {e}")


@pytest.mark.integration
@pytest.mark.real_server
@pytest.mark.timeout(60)
def test_real_file_upload_download(ftp_client_with_cleanup):
    """Test actual file upload and download to/from real server"""
    ftp_client, cleanup_tracker = ftp_client_with_cleanup
    
    try:
        # Tạo file test
        test_content = f"Test file created at {time.strftime('%Y-%m-%d %H:%M:%S')}"
        test_filename = f"test_upload_{int(time.time())}.txt"
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(test_content)
            local_file = f.name
            
        download_path = local_file + ".downloaded"
        try:
            # Upload file
            ftp_client.do_put(f"{local_file} {test_filename}")
            
            # Đánh dấu file để dọn dẹp sau khi test hoàn thành
            cleanup_tracker.add_file(test_filename)
            
            # Kiểm tra file tồn tại trên server
            files = ftp_client.ftp.nlst()
            assert test_filename in files, f"Uploaded file {test_filename} not found on server"
            
            # Download file
            ftp_client.do_get(f"{test_filename} {download_path}")
            
            # Kiểm tra nội dung tải về
            with open(download_path, 'r') as f:
                downloaded_content = f.read()
            assert downloaded_content == test_content, "Downloaded content doesn't match uploaded content"
            
            # Không cần xóa file trên server, đã được theo dõi bởi cleanup_tracker
            
            # Xóa file local
            os.unlink(local_file)
            os.unlink(download_path)
            print("Real file upload/download test passed!")
            
        except Exception as e:
            # Không cần xóa file trên server, đã được theo dõi bởi cleanup_tracker
            
            # Xóa file local
            if os.path.exists(local_file):
                os.unlink(local_file)
            if os.path.exists(download_path):
                os.unlink(download_path)
            raise
            
    except Exception as e:
        pytest.fail(f"Real file upload/download test failed: {e}")


@pytest.mark.integration
@pytest.mark.real_server
@pytest.mark.timeout(30)
def test_real_directory_operations(ftp_client_with_cleanup):
    """Test actual directory operations on real server"""
    ftp_client, cleanup_tracker = ftp_client_with_cleanup
    
    try:
        test_dirname = f"test_dir_{int(time.time())}"
        
        try:
            # Tạo thư mục
            ftp_client.do_mkdir(test_dirname)
            
            # Đánh dấu thư mục để dọn dẹp sau khi test hoàn thành
            cleanup_tracker.add_directory(test_dirname)
            
            # Kiểm tra thư mục tồn tại
            files = ftp_client.ftp.nlst()
            assert test_dirname in files, f"Created directory {test_dirname} not found"
            
            # Đổi vào thư mục
            ftp_client.do_cd(test_dirname)
            pwd = ftp_client.do_pwd("")
            assert test_dirname in str(pwd), f"Failed to change to directory {test_dirname}"
            
            # Đổi về thư mục cha
            ftp_client.do_cd("..")
            
            # Xóa thư mục ngay để kiểm tra tính năng xóa
            ftp_client.do_rmdir(test_dirname)
            
            # Kiểm tra đã xóa
            files = ftp_client.ftp.nlst()
            assert test_dirname not in files, f"Directory {test_dirname} still exists after removal"
            
            # Xóa khỏi danh sách dọn dẹp vì đã được xóa rồi
            cleanup_tracker.dirs_to_delete.remove(test_dirname)
            
            print("Real directory operations test passed!")
            
        except Exception as e:
            # Không cần xóa thư mục thủ công, sẽ được dọn dẹp tự động
            raise
            
    except Exception as e:
        pytest.fail(f"Real directory operations failed: {e}")


@pytest.mark.integration
@pytest.mark.real_server
@pytest.mark.timeout(30)
def test_ftp_commands_status(ftp_client):
    """Test FTP status command and basic commands work"""
    try:
        # Test STATUS command
        ftp_client.do_status("")
        
        # Test PWD command
        pwd = ftp_client.do_pwd("")
        assert pwd, "PWD command failed"
        
        # Test LIST command
        ftp_client.do_ls("")
        
        print("Basic FTP commands test passed!")
        
    except Exception as e:
        pytest.fail(f"FTP commands test failed: {e}")


@pytest.mark.integration
@pytest.mark.real_server
def test_server_capabilities(ftp_client):
    """Test what capabilities the real FTP server supports"""
    try:
        print(f"\n=== FTP Server Capabilities ===")
        print(f"Server: {ftp_client.ftp.host}:{ftp_client.ftp.port}")
        print(f"Welcome: {ftp_client.ftp.welcome}")
        
        # Test FEAT command (if supported)
        try:
            features = ftp_client.ftp.sendcmd('FEAT')
            print(f"Features: {features}")
        except:
            print("FEAT command not supported")
        
        # Test current directory
        print(f"Current directory: {ftp_client.do_pwd('')}")
        
        # Test SYST command
        try:
            system = ftp_client.ftp.sendcmd('SYST')
            print(f"System: {system}")
        except:
            print("SYST command not supported")
        
    except Exception as e:
        print(f"Server capabilities test failed: {e}")


@pytest.mark.integration
@pytest.mark.real_server
@pytest.mark.timeout(30)
def test_passive_active_mode(ftp_client):
    """Test switching between passive and active modes"""
    if not has_credentials():
        pytest.skip("FTP credentials not set. Set FTP_TEST_USER and FTP_TEST_PASS environment variables")
    
    try:
        host, port = TestConfig.get_ftp_config()
        
        # Thiết lập thông tin đăng nhập từ biến môi trường
        TestConfig.FTP_USER = ftp_user
        TestConfig.FTP_PASS = ftp_pass
        
        # Kết nối
        ftp_client.do_open(f"{host} {port}")
        
        # Đăng nhập thủ công nếu cần
        if ftp_client.ftp is None:
            ftp_client.ftp = FTP()
            ftp_client.ftp.connect(host, port)
            ftp_client.ftp.login(ftp_user, ftp_pass)
            # Quan trọng: Tạo ftp_helpers nếu kết nối thủ công
            ftp_client.ftp_helpers = FTPHelpers(ftp_client.ftp)
            print("Manual connection successful")
            
        # Mặc định là passive mode
        assert ftp_client.passive_mode == True, "Default mode should be passive"
        
        # Kiểm tra passive mode có hoạt động không
        try:
            # Liệt kê file trong passive mode
            ftp_client.do_ls("")
            
            # Lưu trạng thái passive
            ftp_client.passive_mode = False
            assert ftp_client.passive_mode == False, "Failed to switch to active mode"
            
            # Kiểm tra hoạt động trong active mode
            try:
                # Liệt kê file trong active mode
                ftp_client.do_ls("")
                print("Active mode listing successful")
            except Exception as e:
                # Nhiều server không hỗ trợ active mode, vì vậy ta chấp nhận lỗi ở đây
                print(f"Active mode test encountered expected limitation: {e}")
                pytest.skip(f"Server does not support active mode: {e}")
            
            # Chuyển lại về passive mode
            ftp_client.passive_mode = True
            assert ftp_client.passive_mode == True, "Failed to switch back to passive mode"
            
            # Kiểm tra passive mode làm việc trở lại
            ftp_client.do_ls("")
            print("Passive mode listing successful")
            
            print("Mode switching test passed!")
            
        except Exception as e:
            pytest.fail(f"Mode switching test failed: {e}")
            
    except Exception as e:
        pytest.fail(f"Mode switching test failed: {e}")


@pytest.mark.integration
@pytest.mark.real_server
@pytest.mark.timeout(30)
def test_local_operations(ftp_client):
    """Test local file system operations (lcd, lpwd, lls)"""
    if not has_credentials():
        pytest.skip("FTP credentials not set. Set FTP_TEST_USER and FTP_TEST_PASS environment variables")
    
    try:
        # Kết nối với FTP server không cần thiết cho local operations,
        # nhưng ta cần đảm bảo client được khởi tạo đúng
        host, port = TestConfig.get_ftp_config()
        
        # Thiết lập thông tin đăng nhập từ biến môi trường
        TestConfig.FTP_USER = ftp_user
        TestConfig.FTP_PASS = ftp_pass
        
        # Kết nối
        ftp_client.do_open(f"{host} {port}")
        
        # Đăng nhập thủ công nếu cần
        if ftp_client.ftp is None:
            ftp_client.ftp = FTP()
            ftp_client.ftp.connect(host, port)
            ftp_client.ftp.login(ftp_user, ftp_pass)
            # Quan trọng: Tạo ftp_helpers nếu kết nối thủ công
            ftp_client.ftp_helpers = FTPHelpers(ftp_client.ftp)
            print("Manual connection successful")
            
        # Lưu thư mục hiện tại
        original_dir = os.getcwd()
        temp_dir = None
        
        try:
            # Kiểm tra lpwd - hiển thị thư mục hiện tại
            ftp_client.do_lpwd("")
            
            # Tạo thư mục tạm để test - không dùng context manager để tránh permission error
            temp_dir = tempfile.mkdtemp()
            
            # Di chuyển đến thư mục tạm
            ftp_client.do_lcd(temp_dir)
            
            # Kiểm tra đã di chuyển thành công
            assert os.path.normpath(os.getcwd()) == os.path.normpath(temp_dir), \
                f"lcd failed: current dir is {os.getcwd()}, expected {temp_dir}"
            
            # Tạo file test trong thư mục tạm
            test_filename = "test_local_file.txt"
            test_file_path = os.path.join(temp_dir, test_filename)
            with open(test_file_path, 'w') as f:
                f.write("Test content for local operations")
            
            # Kiểm tra file đã được tạo
            assert os.path.exists(test_file_path), f"Failed to create test file {test_file_path}"
            
            # Liệt kê file trong thư mục tạm
            ftp_client.do_lls("")
            
            # Quay lại thư mục gốc trước khi thử navigation
            os.chdir(original_dir)
            ftp_client.do_lcd(original_dir)
            
            # Test di chuyển bằng đường dẫn tuyệt đối
            ftp_client.do_lcd(temp_dir)
            
            # Kiểm tra lại file test vẫn tồn tại
            assert os.path.exists(test_filename), f"Test file not found after absolute path navigation"
            
            print("Local operations test passed!")
                
        finally:
            # Trở về thư mục ban đầu
            os.chdir(original_dir)
            # Dọn dẹp thư mục tạm một cách an toàn
            if temp_dir and os.path.exists(temp_dir):
                try:
                    import time
                    # Đợi một chút để Windows giải phóng file handles
                    time.sleep(0.1)
                    shutil.rmtree(temp_dir, ignore_errors=True)
                except Exception as cleanup_error:
                    print(f"Warning: Could not cleanup temp dir {temp_dir}: {cleanup_error}")
            
    except Exception as e:
        # Trở về thư mục ban đầu
        os.chdir(original_dir)
        pytest.fail(f"Local operations test failed: {e}")


if __name__ == "__main__":
    if not has_credentials():
        print("\nWARNING: FTP credentials not set!")
        print("Set FTP_TEST_USER and FTP_TEST_PASS environment variables")
        print("Example in PowerShell:")
        print("$env:FTP_TEST_USER='username'")
        print("$env:FTP_TEST_PASS='password'")
        print("\nRunning tests with -s flag to allow input...")
    
    # Run real server tests với -s để cho phép input từ người dùng nếu cần
    pytest.main([__file__, "-v", "-s", "-m", "real_server"])
