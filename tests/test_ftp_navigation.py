"""
Test FTP directory navigation capabilities
"""

import pytest
import os
import tempfile
import time
import sys
from pathlib import Path

# Add Client directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "Client"))

from test_config import TestConfig
from Client.ftp_command import FTPCommands
from Client.ftp_helpers import FTPHelpers

# Reuse fixtures from test_real_server.py
from test_real_server import ftp_client, has_credentials


@pytest.mark.integration
@pytest.mark.real_server
@pytest.mark.timeout(30)
def test_directory_navigation(ftp_client_with_cleanup):
    """Test directory navigation (cd/pwd) using the FTP client fixture"""
    ftp_client, cleanup_tracker = ftp_client_with_cleanup
    
    try:
        # Tạo thư mục tạm để test navigation
        timestamp = int(time.time())
        test_dir1 = f"test_nav1_{timestamp}"
        test_dir2 = f"test_nav2_{timestamp}"
        
        try:
            # Lưu thư mục ban đầu
            initial_dir = ftp_client.do_pwd("")
            
            # Tạo thư mục thử nghiệm
            ftp_client.do_mkdir(test_dir1)
            ftp_client.do_mkdir(test_dir2)
            
            # Đánh dấu thư mục để dọn dẹp
            cleanup_tracker.add_directory(test_dir1)
            cleanup_tracker.add_directory(test_dir2)
            
            # Thử di chuyển vào thư mục 1
            ftp_client.do_cd(test_dir1)
            current_dir = ftp_client.do_pwd("")
            assert test_dir1 in str(current_dir), f"Failed to navigate to {test_dir1}"
            
            # Thử tạo file trong thư mục 1
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
                tmp.write("Test file for navigation")
                local_path = tmp.name
            
            try:
                # Upload file vào thư mục hiện tại (test_dir1)
                remote_filename = f"nav_test_file_{timestamp}.txt"
                ftp_client.do_put(f"{local_path} {remote_filename}")
                
                # Đánh dấu file để dọn dẹp
                cleanup_tracker.add_file(f"{test_dir1}/{remote_filename}")
                
                # Kiểm tra file đã được upload
                files = ftp_client.ftp.nlst()
                assert remote_filename in files, f"Uploaded file not found in {test_dir1}"
                
                # Quay lại thư mục gốc
                ftp_client.do_cd("..")
                
                # Di chuyển vào thư mục 2
                ftp_client.do_cd(test_dir2)
                current_dir = ftp_client.do_pwd("")
                assert test_dir2 in str(current_dir), f"Failed to navigate to {test_dir2}"
                
                # Quay về thư mục gốc
                ftp_client.do_cd("/")
                root_dir = ftp_client.do_pwd("")
                assert "/" in str(root_dir), "Failed to return to root directory"
                
                print("Directory navigation test passed!")
                
            finally:
                # Cleanup: Xóa file local
                try:
                    os.unlink(local_path)
                except:
                    pass
                
                # Không cần cleanup server files/dirs - sẽ được tự động dọn dẹp bởi cleanup_tracker
        
        except Exception as e:
            pytest.fail(f"Directory navigation test failed: {e}")
            
    except Exception as e:
        pytest.fail(f"Directory navigation test failed: {e}")


if __name__ == "__main__":
    if not has_credentials():
        print("\nWARNING: FTP credentials not set!")
        print("Set FTP_TEST_USER and FTP_TEST_PASS environment variables")
        exit(1)
        
    pytest.main([__file__, "-v", "-s"])
