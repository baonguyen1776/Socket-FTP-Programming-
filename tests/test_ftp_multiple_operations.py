"""
Test FTP multiple file operations (mget/mput)
"""

import pytest
import os
import tempfile
import shutil
import time
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
@pytest.mark.timeout(60)
def test_multiple_file_upload_download(ftp_client_with_cleanup):
    """Test multiple file operations (mput/mget) with cleanup tracking"""
    ftp_client, cleanup_tracker = ftp_client_with_cleanup
    
    # Mock virus scanner để test nhanh hơn
    class MockVirusScanner:
        def scan_file(self, filepath):
            return True, "OK - file is clean"
    
    original_scanner = ftp_client.virus_scanner
    ftp_client.virus_scanner = MockVirusScanner()
    
    try:
        # Tạo thư mục tạm để test
        timestamp = int(time.time())
        test_dir = f"test_mput_mget_{timestamp}"
        
        # Tạo thư mục test trên server
        ftp_client.do_mkdir(test_dir)
        cleanup_tracker.add_directory(test_dir)
        
        # Di chuyển vào thư mục test
        ftp_client.do_cd(test_dir)
        
        # Tạo nhiều file test để upload
        temp_dir = tempfile.mkdtemp()
        try:
            # Tạo nhiều file test
            file_names = []
            for i in range(3):
                file_name = f"mput_test_file_{i}_{timestamp}.txt"
                file_path = os.path.join(temp_dir, file_name)
                with open(file_path, 'w') as f:
                    f.write(f"Test content for multiple upload file {i}\nTimestamp: {timestamp}")
                file_names.append(file_name)
            
            # Chuyển vào thư mục tạm
            original_dir = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Upload nhiều file bằng mput
                pattern = f"mput_test_file_*_{timestamp}.txt"
                ftp_client.do_mput(pattern)
                
                # Đăng ký các file để cleanup
                for file_name in file_names:
                    cleanup_tracker.add_file(f"{test_dir}/{file_name}")
                
                # Kiểm tra các file đã được upload
                files = ftp_client.ftp.nlst()
                for file_name in file_names:
                    assert file_name in files, f"File {file_name} not found after mput"
                
                # Download nhiều file bằng mget (mget luôn download vào Config.DOWNLOAD_DIR)
                from config import Config
                ftp_client.do_mget(pattern)
                
                # Kiểm tra các file đã được download trong Config.DOWNLOAD_DIR
                for file_name in file_names:
                    downloaded_file = os.path.join(Config.DOWNLOAD_DIR, file_name)
                    assert os.path.exists(downloaded_file), f"File {file_name} not found after mget in {Config.DOWNLOAD_DIR}"
                    
                    # Kiểm tra nội dung file
                    with open(downloaded_file, 'r') as f:
                        content = f.read()
                        assert f"file {file_name.split('_')[3]}" in content, f"Content mismatch in {file_name}"
                    
                    # Dọn dẹp file đã download
                    try:
                        os.remove(downloaded_file)
                    except:
                        pass
                
                print("Multiple file upload/download test passed!")
                
            finally:
                # Quay lại thư mục ban đầu
                os.chdir(original_dir)
                
        finally:
            # Dọn dẹp thư mục tạm local
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            # Quay lại thư mục gốc trên server
            try:
                ftp_client.do_cd("/")
            except:
                pass
    
    except Exception as e:
        pytest.fail(f"Multiple file operations test failed: {e}")
    finally:
        # Khôi phục virus scanner ban đầu
        ftp_client.virus_scanner = original_scanner


@pytest.mark.integration
@pytest.mark.real_server
@pytest.mark.timeout(30)
def test_wildcard_operations(ftp_client_with_cleanup):
    """Test wildcard operations with different patterns"""
    ftp_client, cleanup_tracker = ftp_client_with_cleanup
    
    # Mock virus scanner để test nhanh hơn
    class MockVirusScanner:
        def scan_file(self, filepath):
            return True, "OK - file is clean"
    
    original_scanner = ftp_client.virus_scanner
    ftp_client.virus_scanner = MockVirusScanner()
    
    try:
        # Tạo thư mục test
        timestamp = int(time.time())
        test_dir = f"test_wildcard_{timestamp}"
        
        ftp_client.do_mkdir(test_dir)
        cleanup_tracker.add_directory(test_dir)
        ftp_client.do_cd(test_dir)
        
        # Tạo files với các extension khác nhau
        temp_dir = tempfile.mkdtemp()
        try:
            original_dir = os.getcwd()
            os.chdir(temp_dir)
            
            # Tạo files
            test_files = [
                f"doc_{timestamp}.txt",
                f"data_{timestamp}.csv", 
                f"config_{timestamp}.json",
                f"readme_{timestamp}.md"
            ]
            
            for filename in test_files:
                with open(filename, 'w') as f:
                    f.write(f"Content of {filename}")
            
            # Upload tất cả file .txt
            ftp_client.do_mput(f"*_{timestamp}.txt")
            cleanup_tracker.add_file(f"{test_dir}/doc_{timestamp}.txt")
            
            # Upload tất cả file .csv
            ftp_client.do_mput(f"*_{timestamp}.csv")
            cleanup_tracker.add_file(f"{test_dir}/data_{timestamp}.csv")
            
            # Kiểm tra files đã upload
            files = ftp_client.ftp.nlst()
            assert f"doc_{timestamp}.txt" in files
            assert f"data_{timestamp}.csv" in files
            
            print("Wildcard operations test passed!")
            
        finally:
            os.chdir(original_dir)
            shutil.rmtree(temp_dir, ignore_errors=True)
            
    except Exception as e:
        pytest.fail(f"Wildcard operations test failed: {e}")
    finally:
        # Khôi phục virus scanner ban đầu
        ftp_client.virus_scanner = original_scanner


if __name__ == "__main__":
    if not has_credentials():
        print("\nWARNING: FTP credentials not set!")
        print("Set FTP_TEST_USER and FTP_TEST_PASS environment variables")
        exit(1)
        
    pytest.main([__file__, "-v", "-s"])
