"""
Test FTP active/passive mode switching
"""

import pytest
import os
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
def test_passive_active_mode(ftp_client):
    """Test switching between passive and active modes"""
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
            print("Passive mode listing successful after switching back")
            
            print("Mode switching test passed!")
            
        finally:
            # Restore original mode
            ftp_client.passive_mode = original_mode
            
    except Exception as e:
        pytest.fail(f"Mode switching test failed: {e}")


if __name__ == "__main__":
    if not has_credentials():
        print("\nWARNING: FTP credentials not set!")
        print("Set FTP_TEST_USER and FTP_TEST_PASS environment variables")
        exit(1)
        
    pytest.main([__file__, "-v", "-s"])
