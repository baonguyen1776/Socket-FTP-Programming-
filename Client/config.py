import os
import logging

class Config:
    # Cấu hình kết nối FTP
    FTP_HOST = '127.0.0.1'
    FTP_PORT = 21
    # FTP_USERNAME và FTP_PASSWORD sẽ được nhập khi kết nối

    # Cấu hình ClamAV Agent
    CLAMAV_AGENT_HOST = '127.0.0.1'  # Địa chỉ IP của ClamAV Agent
    CLAMAV_AGENT_PORT = 65432       # Cổng của ClamAV Agent (cập nhật theo mã bạn cung cấp)
    CLAMAV_BUFFER_SIZE = 4096      # Kích thước bộ đệm khi gửi/nhận dữ liệu

    # Cấu hình Logging
    LOG_FILE = 'ftp_client.log'    # Tên file log
    LOG_LEVEL = logging.INFO       # Mức độ log (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    # Cấu hình khác
    DOWNLOAD_DIR = os.path.join(os.getcwd(), 'downloads') # Thư mục mặc định để tải xuống


