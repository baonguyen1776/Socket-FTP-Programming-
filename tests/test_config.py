"""
File cấu hình test chứa các settings cho FTP server và ClamAV testing
"""

import os

class TestConfig:
    # Cấu hình FTP Server  
    FTP_HOST = '127.0.0.1'  # Đồng bộ với Client/config.py
    FTP_PORT = 21
    FTP_USERNAME = None  # Sẽ được nhắc nhập
    FTP_PASSWORD = None  # Sẽ được nhắc nhập
    
    # Cấu hình ClamAV Agent  
    CLAMAV_HOST = '127.0.0.1'
    CLAMAV_PORT = 9001
    
    # Cài đặt timeout
    FTP_TIMEOUT = 6000
    CLAMAV_TIMEOUT = 200
    
    @classmethod
    def get_credentials(cls):
        """Lấy thông tin đăng nhập FTP chỉ từ biến môi trường"""
        username = os.getenv('FTP_TEST_USER')
        password = os.getenv('FTP_TEST_PASS')
        
        if not username or not password:
            raise ValueError(
                "Biến môi trường FTP_TEST_USER và FTP_TEST_PASS phải được đặt.\n"
                "Ví dụ:\n"
                "  $env:FTP_TEST_USER=\"your_username\"\n"
                "  $env:FTP_TEST_PASS=\"your_password\""
            )
        
        cls.FTP_USERNAME = username
        cls.FTP_PASSWORD = password
        return username, password
    
    @classmethod
    def get_ftp_config(cls):
        """Lấy cấu hình FTP server"""
        host = os.getenv('FTP_TEST_HOST', cls.FTP_HOST)
        port = int(os.getenv('FTP_TEST_PORT', cls.FTP_PORT))
        return host, port
