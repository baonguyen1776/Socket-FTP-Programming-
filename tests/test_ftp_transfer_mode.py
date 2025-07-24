"""
Test chuyển đổi giữa chế độ active/passive của FTP
"""

import pytest
import os
import sys
import time
import tempfile
from pathlib import Path

# Thêm thư mục Client vào path
sys.path.insert(0, str(Path(__file__).parent.parent / "Client"))

from test_config import TestConfig

# Import functions để kiểm tra credentials
def has_credentials():
    """Kiểm tra nếu đã có thông tin đăng nhập FTP"""
    ftp_user = os.environ.get('FTP_TEST_USER')
    ftp_pass = os.environ.get('FTP_TEST_PASS')
    return ftp_user is not None and ftp_pass is not None


@pytest.mark.integration
@pytest.mark.real_server
@pytest.mark.timeout(30)
def test_passive_active_mode(ftp_client):
    """Test chuyển đổi giữa chế độ passive và active"""
    # Thiết lập credentials nếu chưa kết nối
    if not ftp_client.ftp:
        if not has_credentials():
            pytest.skip("FTP credentials not set")
        
        ftp_user = os.environ.get('FTP_TEST_USER')
        ftp_pass = os.environ.get('FTP_TEST_PASS')
        TestConfig.FTP_USER = ftp_user
        TestConfig.FTP_PASS = ftp_pass
        
        host, port = TestConfig.get_ftp_config()
        ftp_client.do_open(f"{host} {port}")
    
    try:
        # Lưu trạng thái passive ban đầu
        original_mode = ftp_client.passive_mode
        
        try:
            # Đảm bảo đang ở passive mode
            ftp_client.passive_mode = True
            assert ftp_client.passive_mode == True, "Failed to set passive mode"
            
            # Kiểm tra passive mode có hoạt động không
            ftp_client.do_ls("")
            print("Passive mode listing successful")
            
            # Chuyển sang active mode
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
            print("Passive mode listing successful after switching back")
            
            print("Mode switching test passed!")
            
        finally:
            # Khôi phục chế độ ban đầu
            ftp_client.passive_mode = original_mode
            
    except Exception as e:
        pytest.fail(f"Mode switching test failed: {e}")


if __name__ == "__main__":
    if not has_credentials():
        print("\nWARNING: FTP credentials not set!")
        print("Set FTP_TEST_USER and FTP_TEST_PASS environment variables")
        exit(1)
        
    pytest.main([__file__, "-v", "-s"])
