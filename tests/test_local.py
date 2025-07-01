"""
Pytest-based tests for local operations (LCD)
Test suite for FTP client local directory operations
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path


@pytest.mark.local_ops
class TestLocalOperations:
    """Test local directory operations (LCD command)"""
    
    def setup_method(self):
        """Thiết lập trước mỗi test - lưu thư mục hiện tại"""
        self.original_dir = os.getcwd()
        self.temp_dir = None
    
    def teardown_method(self):
        """Dọn dẹp sau mỗi test - khôi phục thư mục gốc"""
        os.chdir(self.original_dir)
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @pytest.mark.unit
    def test_client_creation(self, ftp_client):
        """Test khởi tạo FTP client thành công"""
        assert ftp_client is not None
        assert hasattr(ftp_client, 'do_lcd')
    
    @pytest.mark.unit
    def test_current_directory_check(self, ftp_client):
        """Test kiểm tra thư mục hiện tại"""
        current_dir = os.getcwd()
        assert os.path.exists(current_dir)
        assert os.path.isdir(current_dir)
    
    @pytest.mark.unit
    def test_temp_directory_creation(self, ftp_client):
        """Test tạo thư mục tạm thời"""
        self.temp_dir = tempfile.mkdtemp(prefix="ftp_test_")
        assert os.path.exists(self.temp_dir)
        assert os.path.isdir(self.temp_dir)
    
    @pytest.mark.unit
    def test_lcd_command_basic(self, ftp_client):
        """Test lệnh LCD cơ bản - thay đổi thư mục"""
        # Tạo thư mục tạm để test
        self.temp_dir = tempfile.mkdtemp(prefix="ftp_test_")
        
        # Thực hiện lệnh LCD
        result = ftp_client.do_lcd(self.temp_dir)
        
        # Kiểm tra kết quả
        current_dir = os.getcwd()
        assert current_dir == os.path.abspath(self.temp_dir)
    
    @pytest.mark.unit
    def test_lcd_relative_path(self, ftp_client):
        """Test LCD với đường dẫn tương đối"""
        # Tạo thư mục tạm với cấu trúc con
        self.temp_dir = tempfile.mkdtemp(prefix="ftp_test_")
        sub_dir = os.path.join(self.temp_dir, "subdir")
        os.makedirs(sub_dir)
        
        # Chuyển đến thư mục con
        ftp_client.do_lcd(sub_dir)
        assert os.getcwd() == os.path.abspath(sub_dir)
        
        # Sử dụng .. để quay lại thư mục cha
        ftp_client.do_lcd("..")
        assert os.getcwd() == os.path.abspath(self.temp_dir)
    
    @pytest.mark.unit
    def test_lcd_error_handling(self, ftp_client):
        """Test xử lý lỗi LCD với thư mục không tồn tại"""
        original_dir = os.getcwd()
        non_existent_dir = "/nonexistent/directory/path"
        
        # Thực hiện LCD với thư mục không tồn tại
        ftp_client.do_lcd(non_existent_dir)
        
        # Thư mục hiện tại không thay đổi
        current_dir = os.getcwd()
        assert current_dir == original_dir
    
    @pytest.mark.unit
    def test_lcd_empty_argument(self, ftp_client):
        """Test LCD với tham số rỗng"""
        original_dir = os.getcwd()
        
        # Thực hiện LCD với tham số rỗng
        ftp_client.do_lcd("")
        
        # Thư mục hiện tại không thay đổi
        current_dir = os.getcwd()
        assert current_dir == original_dir
    
    @pytest.mark.unit
    def test_lcd_absolute_path(self, ftp_client):
        """Test LCD với đường dẫn tuyệt đối"""
        # Tạo thư mục tạm
        self.temp_dir = tempfile.mkdtemp(prefix="ftp_test_")
        abs_path = os.path.abspath(self.temp_dir)
        
        # Thực hiện LCD với đường dẫn tuyệt đối
        ftp_client.do_lcd(abs_path)
        
        # Kiểm tra thư mục hiện tại
        current_dir = os.getcwd()
        assert current_dir == abs_path
    
    @pytest.mark.unit
    def test_lcd_path_with_spaces(self, ftp_client):
        """Test LCD với tên thư mục có khoảng trắng"""
        # Tạo thư mục có tên chứa khoảng trắng
        base_temp = tempfile.mkdtemp(prefix="ftp_test_")
        self.temp_dir = os.path.join(base_temp, "dir with spaces")
        os.makedirs(self.temp_dir)
        
        # Thực hiện LCD
        ftp_client.do_lcd(self.temp_dir)
        
        # Kiểm tra kết quả
        current_dir = os.getcwd()
        assert current_dir == os.path.abspath(self.temp_dir)
        
        # Cleanup
        self.temp_dir = base_temp  # để teardown có thể dọn dẹp


# Standalone test functions (không dùng class)
@pytest.mark.local_ops
@pytest.mark.unit
def test_lcd_directory_tracking(ftp_client):
    """Test theo dõi thay đổi thư mục qua client"""
    original_dir = os.getcwd()
    
    # Tạo thư mục tạm
    temp_dir = tempfile.mkdtemp(prefix="ftp_test_tracking_")
    
    try:
        # Thực hiện thay đổi thư mục
        ftp_client.do_lcd(temp_dir)
        
        # Kiểm tra client có theo dõi được thay đổi không
        current_dir = os.getcwd()
        assert current_dir == os.path.abspath(temp_dir)
        
    finally:
        # Dọn dẹp
        os.chdir(original_dir)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.mark.local_ops
@pytest.mark.integration
def test_lcd_integration_workflow(ftp_client):
    """Test workflow tích hợp với nhiều lệnh LCD"""
    original_dir = os.getcwd()
    
    # Tạo cấu trúc thư mục phức tạp
    base_temp = tempfile.mkdtemp(prefix="ftp_integration_")
    
    try:
        # Tạo cấu trúc: base/level1/level2/
        level1 = os.path.join(base_temp, "level1")
        level2 = os.path.join(level1, "level2")
        os.makedirs(level2)
        
        # Test workflow: base -> level1 -> level2 -> back to base
        ftp_client.do_lcd(base_temp)
        assert os.getcwd() == os.path.abspath(base_temp)
        
        ftp_client.do_lcd("level1")
        assert os.getcwd() == os.path.abspath(level1)
        
        ftp_client.do_lcd("level2")
        assert os.getcwd() == os.path.abspath(level2)
        
        ftp_client.do_lcd("../..")
        assert os.getcwd() == os.path.abspath(base_temp)
        
    finally:
        # Dọn dẹp
        os.chdir(original_dir)
        if os.path.exists(base_temp):
            shutil.rmtree(base_temp, ignore_errors=True)


if __name__ == "__main__":
    # Chạy test trực tiếp
    pytest.main([__file__, "-v"])
