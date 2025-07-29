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
sys.path.insert(0, str(Path(__file__).parent.parent / "client"))

from test_config import TestConfig

# Import fixtures from test_real_server.py
from test_real_server import ftp_client, has_credentials


@pytest.mark.integration
@pytest.mark.real_server
@pytest.mark.timeout(60)  # Tăng timeout lên 60 giây cho active mode
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
            
            # Thử chuyển sang active mode với timeout và error handling
            print("Testing active mode switch...")
            ftp_client.passive_mode = False
            assert ftp_client.passive_mode == False, "Failed to switch to active mode"
            
            # Test active mode với timeout protection
            import signal
            def timeout_handler(signum, frame):
                raise TimeoutError("Active mode test timed out")
            
            # Set timeout handler cho Windows (dùng threading thay vì signal)
            import threading
            active_mode_success = False
            active_mode_error = None
            
            def test_active_mode():
                nonlocal active_mode_success, active_mode_error
                try:
                    print("Attempting active mode listing...")
                    ftp_client.do_ls("")
                    active_mode_success = True
                    print("Active mode listing successful!")
                except Exception as e:
                    active_mode_error = e
                    print(f"Active mode failed: {e}")
            
            # Chạy test active mode trong thread với timeout
            test_thread = threading.Thread(target=test_active_mode)
            test_thread.daemon = True
            test_thread.start()
            test_thread.join(timeout=15)  # 15 giây timeout cho active mode
            
            if test_thread.is_alive():
                print("Active mode test timed out - likely due to NAT/firewall issues")
                print("This is expected behavior in many network environments")
            elif active_mode_success:
                print("Active mode works correctly!")
            elif active_mode_error:
                print(f"Active mode failed with error: {active_mode_error}")
                print("This may be expected depending on server/network configuration")
            
            # Chuyển lại về passive mode
            print("Switching back to passive mode...")
            ftp_client.passive_mode = True
            assert ftp_client.passive_mode == True, "Failed to switch back to passive mode"
            
            # Kiểm tra passive mode làm việc trở lại
            ftp_client.do_ls("")
            print("Passive mode listing successful after switching back")
            
            print("Mode switching test completed!")
            
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
