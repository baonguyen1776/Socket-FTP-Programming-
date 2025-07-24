"""
Gói Test Suite cho FTP Client - Phiên bản Pytest

Test suite hiện đại sử dụng pytest với các tính năng tốt hơn:
- Fixtures tự động và setup/teardown
- Bảo vệ timeout để ngăn chặn treo
- Phân loại test dựa trên marker  
- Báo cáo HTML và output tốt hơn
- Mock testing cho phát triển offline

Cách sử dụng:
    python test_runner.py           # Menu tương tác
    python -m pytest -m unit       # Unit tests nhanh
    python -m pytest -v            # Tất cả tests với output chi tiết
    python test.py quick           # Shortcut cho quick tests
"""

__version__ = "3.0.0-pytest"
__author__ = "FTP Client Test Team"

# Import cấu hình test để truy cập dễ dàng
from .test_config import TestConfig

__all__ = [
    'TestConfig',
    'test_session',
    'test_file', 
    'test_directory',
    'test_local',
    'test_config_validation'
]
