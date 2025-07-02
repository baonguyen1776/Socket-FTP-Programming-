"""
Test FTP client local operations (lcd, lpwd, lls)
"""

import pytest
import os
import tempfile
import sys
from pathlib import Path

# Add Client directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "Client"))

from test_config import TestConfig
from ftp_command import FTPCommands
from ftp_helpers import FTPHelpers

# Reuse fixtures from test_real_server.py
from test_real_server import ftp_client, has_credentials


@pytest.mark.integration
@pytest.mark.real_server
@pytest.mark.timeout(30)
def test_local_operations(ftp_client):
    """Test local file system operations (lcd, lpwd, lls)"""
    try:
        # Lưu thư mục hiện tại
        original_dir = os.getcwd()
        
        try:
            # Kiểm tra lpwd - hiển thị thư mục hiện tại
            ftp_client.do_lpwd("")
            
            # Tạo thư mục tạm để test
            with tempfile.TemporaryDirectory() as temp_dir:
                # Di chuyển đến thư mục tạm
                ftp_client.do_lcd(temp_dir)
                
                # Kiểm tra đã di chuyển thành công
                assert os.path.normpath(os.getcwd()) == os.path.normpath(temp_dir), \
                    f"lcd failed: current dir is {os.getcwd()}, expected {temp_dir}"
                
                # Tạo file test trong thư mục tạm
                test_filename = "test_local_file.txt"
                with open(test_filename, 'w') as f:
                    f.write("Test content for local operations")
                
                # Kiểm tra file đã được tạo
                assert os.path.exists(test_filename), f"Failed to create test file {test_filename}"
                
                # Liệt kê file trong thư mục tạm
                ftp_client.do_lls("")
                
                # Quay lại thư mục gốc
                ftp_client.do_lcd(original_dir)
                assert os.path.normpath(os.getcwd()) == os.path.normpath(original_dir), \
                    f"Failed to return to original directory: {os.getcwd()} != {original_dir}"
                
                print("Local operations test passed!")
                
        finally:
            # Trở về thư mục ban đầu
            os.chdir(original_dir)
            
    except Exception as e:
        # Trở về thư mục ban đầu
        os.chdir(original_dir)
        pytest.fail(f"Local operations test failed: {e}")


if __name__ == "__main__":
    if not has_credentials():
        print("\nWARNING: FTP credentials not set!")
        print("Set FTP_TEST_USER and FTP_TEST_PASS environment variables")
        exit(1)
        
    pytest.main([__file__, "-v", "-s"])
