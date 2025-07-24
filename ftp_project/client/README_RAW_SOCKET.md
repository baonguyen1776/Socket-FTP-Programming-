# RAW SOCKET FTP CLIENT

## 🎯 Giải pháp thay thế ftplib

Vì giảng viên không cho dùng thư viện `ftplib`, tôi đã implement lại toàn bộ FTP client bằng **raw socket** (socket thô).

## 🔧 Kiến trúc

### Raw Socket Functions (raw_socket_ftp.py)
```python
# Các function socket thô chính:
ftp_connect(host, port)       # Kết nối server
ftp_login(user, pass)         # Đăng nhập  
ftp_send_command(cmd)         # Gửi lệnh FTP
ftp_send_line(line)           # Gửi dòng thô
ftp_recv_line()               # Nhận dòng thô
ftp_get_response()            # Nhận phản hồi
ftp_pwd()                     # Lấy thư mục hiện tại
ftp_cwd(dirname)              # Thay đổi thư mục
ftp_mkd(dirname)              # Tạo thư mục
ftp_rmd(dirname)              # Xóa thư mục
ftp_delete(filename)          # Xóa file
ftp_rename(old, new)          # Đổi tên
ftp_size(filename)            # Lấy kích thước
ftp_nlst()                    # List files
ftp_dir()                     # List chi tiết
ftp_retrbinary(cmd, callback) # Download binary
ftp_retrlines(cmd, callback)  # Download ASCII
ftp_storbinary(cmd, file)     # Upload binary
ftp_storlines(cmd, lines)     # Upload ASCII
ftp_make_pasv()               # Passive mode
ftp_make_port()               # Active mode
ftp_transfer_cmd(cmd)         # Data transfer
ftp_quit()                    # Thoát
```

### Wrapper Class
```python
class FTP:
    """Wrapper để tương thích với code cũ"""
    def connect(self, host, port=21, timeout=60)
    def login(self, user, passwd)
    def pwd(self)
    def cwd(self, dirname)
    # ... tất cả methods giống ftplib.FTP
```

## 🚀 Cách sử dụng

### 1. Command Line Client
```bash
python3 client.py
```

### 2. GUI Client  
```bash
python3 main.py
```

### 3. Raw Socket Functions trực tiếp
```python
from raw_socket_ftp import *

# Kết nối
ftp_connect('test.rebex.net', 21)
ftp_login('demo', 'password')

# Thao tác
current_dir = ftp_pwd()
files = ftp_nlst()
ftp_dir()

# Thoát
ftp_quit()
```

### 4. Wrapper Class (tương thích ftplib)
```python
from raw_socket_ftp import FTP

ftp = FTP()
ftp.connect('test.rebex.net', 21)
ftp.login('demo', 'password')
print(ftp.pwd())
files = ftp.nlst()
ftp.quit()
```

## 📁 Files đã cập nhật

- ✅ `raw_socket_ftp.py` - Raw socket implementation
- ✅ `ftp_command.py` - Updated imports  
- ✅ `ftp_helpers.py` - Updated imports
- ✅ `ftp_gui.py` - Updated imports
- ✅ `login_window.py` - Updated imports
- ✅ `tests/test_real_server.py` - Updated imports

## 🔄 Thay đổi chính

**Trước:**
```python
from ftplib import FTP, all_errors, error_perm, error_temp, error_proto
```

**Sau:**
```python
from raw_socket_ftp import FTP, all_errors, error_perm, error_temp, error_proto
```

## ⚡ Tính năng

- ✅ **Raw Socket**: Chỉ dùng `socket.socket()`, không dùng ftplib
- ✅ **Passive Mode**: Hỗ trợ PASV command
- ✅ **Active Mode**: Hỗ trợ PORT command  
- ✅ **Binary Transfer**: Upload/Download file binary
- ✅ **ASCII Transfer**: Upload/Download file text
- ✅ **Directory Operations**: mkdir, rmdir, ls, cd
- ✅ **File Operations**: get, put, delete, rename
- ✅ **Error Handling**: FTP error codes 4xx, 5xx
- ✅ **Multi-line Responses**: Parse FTP multi-line
- ✅ **Compatibility**: Tương thích 100% với code cũ

## 🧪 Test

```bash
# Test import
python3 -c "from raw_socket_ftp import *; print('Raw socket OK!')"

# Test client
python3 -c "from raw_socket_ftp import FTP; from ftp_command import FTPCommands; client = FTPCommands(FTP()); print('Client OK!')"

# Demo
python3 demo_raw_socket.py
```

## 🎯 Lợi ích

1. **Không phụ thuộc ftplib** - Hoàn toàn tự implement
2. **Hiểu rõ giao thức FTP** - Làm từ socket level
3. **Kiểm soát hoàn toàn** - Customize mọi thứ
4. **Tương thích code cũ** - Không cần sửa logic
5. **Dễ debug** - Thấy rõ FTP commands/responses

## 📚 Giao thức FTP được implement

- **Control Connection**: Port 21, gửi/nhận commands
- **Data Connection**: Dynamic port, transfer files
- **Commands**: USER, PASS, PWD, CWD, MKD, RMD, DELE, RNFR, RNTO, SIZE, NLST, LIST, RETR, STOR, PASV, PORT, QUIT
- **Response Codes**: 1xx, 2xx, 3xx, 4xx, 5xx
- **Transfer Modes**: Binary (TYPE I), ASCII (TYPE A)

## 🚀 Kết luận

Giờ bạn có thể nộp bài **KHÔNG DÙNG FTPLIB** mà vẫn có đầy đủ tính năng FTP client!

Tất cả được implement bằng **raw socket** từ đầu, hoàn toàn tự viết.