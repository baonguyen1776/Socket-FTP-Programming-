# 📂 Hướng dẫn chạy pytest đúng đường dẫn

## ✅ CÁCH ĐÚNG - Khuyến nghị

### 1. Luôn chạy từ thư mục ROOT project

```powershell
# Mở PowerShell và chuyển đến thư mục gốc
cd "c:\Users\nguye\OneDrive - VNU-HCMUS\Năm 1\Học kì 3\Mạng pc\projectSocket\Socket-FTP-Programming-"

# Chạy tất cả tests
pytest

# Hoặc với output chi tiết
pytest -v
```

**Tại sao đây là cách tốt nhất?**
- ✅ Python tự động thêm thư mục hiện tại vào PYTHONPATH
- ✅ Có thể import `Client.ftp_command`, `ClamAvAgent.scanner` dễ dàng
- ✅ File `pytest.ini` được nhận diện tự động
- ✅ Đường dẫn relative trong tests hoạt động đúng

## 🔧 CÁC LỆNH CHẠY PYTEST THƯỜNG DÙNG

### Từ thư mục root project:

```powershell
# Chạy tất cả tests
pytest

# Chạy với output chi tiết
pytest -v

# Chạy chỉ tests của Client
pytest tests/client/

# Chạy chỉ tests của ClamAV Agent  
pytest tests/clamav_agent/

# Chạy một file test cụ thể
pytest tests/client/test_virus_scan.py

# Chạy một test method cụ thể
pytest tests/client/test_virus_scan.py::TestVirusScan::test_scan_file_clean

# Chạy với coverage
pytest --cov=Client --cov=ClamAvAgent

# Chạy và dừng ngay khi gặp lỗi đầu tiên
pytest -x

# Chạy chỉ tests bị fail lần trước
pytest --lf
```

## ⚠️ CÁC LỖI THƯỜNG GẶP VÀ CÁCH XỬ LÝ

### Lỗi 1: ModuleNotFoundError

```
ModuleNotFoundError: No module named 'Client'
```

**Nguyên nhân:** Chạy pytest từ thư mục sai
**Giải pháp:** Chuyển về thư mục root project

```powershell
cd "c:\Users\nguye\OneDrive - VNU-HCMUS\Năm 1\Học kì 3\Mạng pc\projectSocket\Socket-FTP-Programming-"
pytest
```

### Lỗi 2: No tests ran matching the given patterns

```
collected 0 items
```

**Nguyên nhân:** Pytest không tìm thấy file tests
**Giải pháp:** Kiểm tra đường dẫn và cấu trúc thư mục

```powershell
# Kiểm tra bạn đang ở đâu
Get-Location

# Liệt kê files
ls tests/

# Chạy với pattern cụ thể
pytest tests/client/test_*.py
```

### Lỗi 3: Import error trong test files

```
ImportError: attempted relative import with no known parent package
```

**Nguyên nhân:** Sử dụng relative imports không đúng
**Giải pháp:** Đảm bảo chạy từ root và sử dụng absolute imports

## 🚀 WORKFLOW PHÁT TRIỂN KHUYẾN NGHỊ

### 1. Mở terminal mới
```powershell
cd "c:\Users\nguye\OneDrive - VNU-HCMUS\Năm 1\Học kì 3\Mạng pc\projectSocket\Socket-FTP-Programming-"
```

### 2. Chạy tests khi phát triển
```powershell
# Quick check - chạy nhanh tất cả tests
pytest

# Khi code Client component
pytest tests/client/ -v

# Khi code ClamAV component  
pytest tests/clamav_agent/ -v

# Khi fix bug - chạy test cụ thể
pytest tests/client/test_ftp_command.py::TestFTPCommands::test_connect_success -v
```

### 3. Trước khi commit
```powershell
# Chạy full test suite với coverage
pytest --cov=Client --cov=ClamAvAgent --cov-report=term-missing

# Đảm bảo 100% tests pass
pytest -v
```

## 📁 CẤU TRÚC ĐƯỜNG DẪN TRONG DỰ ÁN

```
Socket-FTP-Programming-/          ← ROOT: Chạy pytest từ đây
├── pytest.ini                    ← Cấu hình pytest
├── requirements-test.txt          ← Dependencies cho testing
├── Client/                        ← Source code Client
│   ├── ftp_command.py
│   ├── virus_scan.py
│   └── ...
├── ClamAvAgent/                   ← Source code ClamAV Agent
│   ├── scanner.py
│   ├── sever_clam.py
│   └── ...
└── tests/                         ← Test directory (testpaths = tests)
    ├── conftest.py                ← Shared fixtures
    ├── client/                    ← Client tests
    │   ├── test_virus_scan.py
    │   └── test_ftp_command.py
    └── clamav_agent/              ← ClamAV tests
        ├── test_scanner.py
        └── test_server_clam.py
```

## 🎯 TÓM TẮT - QUY TẮC VÀNG

1. **Luôn chạy pytest từ thư mục ROOT project**
2. **Kiểm tra Get-Location trước khi chạy**
3. **Sử dụng đường dẫn absolute trong scripts**
4. **Không chạy pytest từ thư mục Client/ hoặc ClamAvAgent/**
5. **File pytest.ini phải ở thư mục ROOT**

---

💡 **Mẹo nhỏ:** Tạo shortcut hoặc alias để nhanh chóng chuyển đến thư mục project và chạy tests!
