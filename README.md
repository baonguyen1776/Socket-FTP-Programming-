# Secure FTP Client với Virus Scanning sử dụng ClamAV Agent

Dự án này triển khai một FTP client bảo mật tích hợp với ClamAV agent để quét virus trước khi upload file. Hệ thống bao gồm hai thành phần chính: FTP Client và ClamAV Agent.

## Tổng quan hệ thống

1. **FTP Client**: Ứng dụng client FTP tùy chỉnh tương tác với FTP server và ClamAV Agent. Hỗ trợ các lệnh FTP chuẩn và đảm bảo tất cả file được quét virus trước khi upload.
2. **ClamAV Agent**: Thành phần server-side nhận file từ FTP Client, quét bằng `clamscan` utility và trả về kết quả quét (OK hoặc INFECTED).

## Cấu trúc dự án chi tiết

```
Socket-FTP-Programming/
├── README.md                    # File hướng dẫn này
├── run_client.py               # Script chính để chạy FTP Client
├── .gitignore                  # File gitignore
│
├── clamav_agent/               # Thư mục ClamAV Agent
│   ├── __init__.py            # Package initialization
│   ├── main.py                # Entry point chính của ClamAV Agent
│   ├── sever_clam.py          # Server ClamAV Agent chính
│   ├── handler.py             # Xử lý kết nối client
│   └── scanner.py             # Module quét virus
│
├── client/                     # Thư mục FTP Client
│   ├── __init__.py            # Package initialization
│   ├── README_RAW_SOCKET.md   # Tài liệu về raw socket
│   │
│   ├── core/                  # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py          # Cấu hình ứng dụng
│   │   ├── ftp_command.py     # Xử lý lệnh FTP
│   │   ├── ftp_helpers.py     # Các hàm hỗ trợ FTP
│   │   ├── raw_socket_ftp.py  # FTP client sử dụng raw socket
│   │   ├── utils.py           # Tiện ích chung
│   │   └── virus_scan.py      # Tích hợp với ClamAV Agent
│   │
│   ├── ui/                    # User Interface
│   │   ├── __init__.py
│   │   ├── main.py            # Entry point cho GUI
│   │   ├── ftp_gui.py         # Giao diện FTP chính
│   │   └── login_window.py    # Cửa sổ đăng nhập
│   │
│   └── networking/            # Network components
│       ├── __init__.py
│       └── client.py          # Network client utilities
│
└── tests/                      # Thư mục test
    ├── __init__.py            # Test package initialization
    ├── README.md              # Hướng dẫn test
    ├── conftest.py            # Cấu hình pytest
    ├── pytest.ini            # Cấu hình pytest
    ├── requirements.txt       # Dependencies cho testing
    ├── cleanup.py             # Script dọn dẹp test
    ├── test_config.py         # Test cấu hình
    ├── test_ftp_*.py          # Các file test FTP
    ├── test_real_server.py    # Test với server thực
    ├── test_runner.py         # Test runner
    └── reports/               # Thư mục báo cáo test
```

## Yêu cầu hệ thống

### Phần mềm cần thiết:
- **Python 3.7+** (khuyến nghị Python 3.8 trở lên)
- **tkinter** (thường đi kèm với Python, có thể cần cài đặt riêng trên một số hệ thống)
- **ClamAV antivirus engine** (bao gồm `clamscan` utility)
- **FTP Server** (ví dụ: FileZilla Server, vsftpd, hoặc pyftpdlib cho testing)

### Thư viện Python:
- `tkinter` - Cho giao diện đồ họa
- `socket` - Cho kết nối mạng
- `threading` - Cho xử lý đa luồng
- `logging` - Cho ghi log
- `pytest` - Cho testing (tùy chọn)

## Hướng dẫn cài đặt

### 1. Cài đặt ClamAV

**Trên Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install clamav clamav-daemon clamav-freshclam
```

**Trên CentOS/RHEL/Fedora:**
```bash
sudo yum install clamav clamav-update
# hoặc
sudo dnf install clamav clamav-update
```

**Trên macOS (sử dụng Homebrew):**
```bash
brew install clamav
```

**Cập nhật cơ sở dữ liệu virus:**
```bash
sudo freshclam
```

**Khởi động ClamAV daemon (Linux):**
```bash
sudo systemctl start clamav-freshclam
sudo systemctl enable clamav-freshclam
sudo systemctl start clamav-daemon
sudo systemctl enable clamav-daemon
```

### 2. Cài đặt FTP Server (tùy chọn)

#### Sử dụng pyftpdlib (đơn giản cho testing):
```bash
pip install pyftpdlib
```

#### Hoặc cài đặt vsftpd (Linux):
```bash
sudo apt install vsftpd
```

### 3. Chuẩn bị môi trường Python

```bash
# Clone repository (nếu cần)
git clone <repository-url>
cd Socket-FTP-Programming

# Tạo virtual environment (khuyến nghị)
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# hoặc
venv\Scripts\activate     # Windows

# Cài đặt dependencies cho testing (tùy chọn)
pip install -r tests/requirements.txt
```

## Hướng dẫn chạy chương trình

### Bước 1: Khởi động ClamAV Agent

Mở terminal đầu tiên và chạy ClamAV Agent:

```bash
cd Socket-FTP-Programming
python3 clamav_agent/main.py
```

**Output mong đợi:**
```
2024-01-XX XX:XX:XX,XXX - INFO - Starting ClamAV Agent...
2024-01-XX XX:XX:XX,XXX - INFO - Server will listen on 0.0.0.0:9001
2024-01-XX XX:XX:XX,XXX - INFO - ClamAV Agent Server started successfully
2024-01-XX XX:XX:XX,XXX - INFO - Waiting for connections...
```

### Bước 2: Khởi động FTP Server (nếu cần)

#### Sử dụng pyftpdlib (đơn giản):
```bash
# Mở terminal thứ hai
python3 -m pyftpdlib -p 21 -u user -P password -d /tmp/ftp
```

#### Hoặc sử dụng FTP server có sẵn
Đảm bảo FTP server đang chạy và có tài khoản user để kết nối.

### Bước 3: Khởi động FTP Client

Mở terminal thứ ba và chạy FTP Client:

#### Chạy với giao diện đồ họa (GUI):
```bash
cd Socket-FTP-Programming
python3 run_client.py --gui
```

#### Chạy với giao diện dòng lệnh (CLI):
```bash
cd Socket-FTP-Programming
python3 run_client.py --cli
```

#### Chạy mặc định (CLI):
```bash
cd Socket-FTP-Programming
python3 run_client.py
```

## Cấu hình hệ thống

### Cấu hình ClamAV Agent

Chỉnh sửa file `clamav_agent/main.py`:
```python
HOST = '0.0.0.0'    # Địa chỉ IP để lắng nghe
PORT = 9001         # Cổng để lắng nghe
```

### Cấu hình FTP Client

Chỉnh sửa file `client/core/config.py`:
```python
class Config:
    # Cấu hình FTP Server
    FTP_HOST = '127.0.0.1'      # Địa chỉ FTP server
    FTP_PORT = 21               # Cổng FTP server
    
    # Cấu hình ClamAV Agent
    CLAMAV_AGENT_HOST = '127.0.0.1'  # Địa chỉ ClamAV Agent
    CLAMAV_AGENT_PORT = 9001         # Cổng ClamAV Agent
    
    # Thư mục download
    DOWNLOAD_DIR = os.path.join(os.getcwd(), 'downloads')
```

## Hướng dẫn sử dụng

### 1. Kết nối FTP

**Với GUI:**
1. Nhập thông tin FTP server (host, port, username, password)
2. Nhập thông tin ClamAV Agent (host, port)
3. Click "Connect"

**Với CLI:**
```
ftp> open <host> <port>
Username: <username>
Password: <password>
```

### 2. Các lệnh FTP hỗ trợ

| Lệnh | Mô tả | Ví dụ |
|------|-------|-------|
| `ls` | Liệt kê file/thư mục | `ls` |
| `cd <dir>` | Chuyển thư mục | `cd documents` |
| `pwd` | Hiển thị thư mục hiện tại | `pwd` |
| `mkdir <dir>` | Tạo thư mục | `mkdir newfolder` |
| `rmdir <dir>` | Xóa thư mục | `rmdir oldfolder` |
| `delete <file>` | Xóa file | `delete oldfile.txt` |
| `rename <old> <new>` | Đổi tên file | `rename old.txt new.txt` |
| `get <file>` | Download file | `get document.pdf` |
| `put <file>` | Upload file (có quét virus) | `put image.jpg` |
| `mget <pattern>` | Download nhiều file | `mget *.txt` |
| `mput <pattern>` | Upload nhiều file (có quét virus) | `mput *.pdf` |
| `help` | Hiển thị trợ giúp | `help` |
| `quit` | Thoát | `quit` |

### 3. Quét virus tự động

Khi upload file (`put` hoặc `mput`), hệ thống sẽ:
1. Gửi file đến ClamAV Agent
2. ClamAV Agent quét file bằng `clamscan`
3. Trả về kết quả: OK hoặc INFECTED
4. Chỉ upload file nếu kết quả là OK

## Testing

### Chạy test suite:
```bash
cd tests
python3 -m pytest -v
```

### Chạy test cụ thể:
```bash
python3 -m pytest test_ftp_navigation.py -v
```

### Tạo báo cáo test:
```bash
python3 -m pytest --html=reports/report.html
```

## Ví dụ sử dụng

### Test với file sạch:
1. Tạo file text: `echo "Hello World" > test.txt`
2. Upload: `put test.txt`
3. Kết quả: File được upload thành công

### Test với file virus (EICAR):
1. Tạo file EICAR:
```bash
echo 'X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*' > eicar.txt
```
2. Upload: `put eicar.txt`
3. Kết quả: Upload bị từ chối, hiển thị cảnh báo virus

## Troubleshooting

### Lỗi thường gặp:

1. **ClamAV Agent không khởi động được:**
   - Kiểm tra ClamAV đã được cài đặt: `clamscan --version`
   - Kiểm tra port 9001 có bị chiếm: `netstat -tulpn | grep 9001`

2. **FTP Client không kết nối được:**
   - Kiểm tra FTP server đang chạy
   - Kiểm tra firewall settings
   - Kiểm tra username/password

3. **Quét virus không hoạt động:**
   - Kiểm tra ClamAV Agent đang chạy
   - Kiểm tra cấu hình CLAMAV_AGENT_HOST và PORT
   - Cập nhật virus database: `sudo freshclam`

4. **GUI không hiển thị:**
   - Cài đặt tkinter: `sudo apt install python3-tkinter`
   - Sử dụng CLI mode thay thế

### Log files:
- FTP Client: `ftp_client.log`
- ClamAV Agent: Console output

## Tính năng nâng cao

- **Multi-threading**: Hỗ trợ xử lý đồng thời nhiều kết nối
- **Raw Socket**: Sử dụng raw socket implementation
- **Graceful shutdown**: Tắt server một cách an toàn
- **Comprehensive logging**: Ghi log chi tiết cho debugging
- **Extensive testing**: Test suite đầy đủ với pytest

## Bảo mật

- Tất cả file upload đều được quét virus
- Kết nối an toàn giữa client và agent
- Validation đầu vào để tránh injection attacks
- Graceful error handling

## Đóng góp

1. Fork repository
2. Tạo feature branch
3. Commit changes
4. Push to branch
5. Tạo Pull Request

## License

[Thêm thông tin license nếu có]

---

**Lưu ý:** Đây là phần mềm giáo dục. Trong môi trường production, cần thêm các biện pháp bảo mật như SSL/TLS, authentication mạnh hơn, và monitoring.
