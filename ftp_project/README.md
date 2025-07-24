# FTP Project - Raw Socket Implementation

## 🎯 Giải pháp thay thế ftplib

Project này implement lại toàn bộ FTP client bằng **raw socket** (không sử dụng thư viện ftplib).

## 📁 Cấu trúc Project

```
ftp_project/
│
├── client/
│   ├── core/                    # Core FTP logic
│   │   ├── raw_socket_ftp.py   # Raw socket FTP implementation
│   │   ├── ftp_command.py      # Command line interface
│   │   ├── ftp_helpers.py      # Helper functions
│   │   ├── virus_scan.py       # Virus scanning
│   │   ├── config.py           # Configuration
│   │   └── utils.py            # Utilities
│   │
│   ├── ui/                     # GUI components
│   │   ├── ftp_gui.py         # Main GUI
│   │   ├── login_window.py    # Login dialog
│   │   └── main.py            # GUI entry point
│   │
│   ├── networking/            # Network utilities
│   │   └── client.py          # Network client
│   │
│   └── downloads/             # Download directory
│
├── clamav_agent/              # Virus scanning agent
│   ├── handler.py             # Request handler
│   ├── scanner.py             # Virus scanner
│   ├── sever_clam.py         # ClamAV server
│   ├── main.py               # Agent entry point
│   └── temp_scan_files/      # Temporary scan files
│
├── tests/                     # Test files
│   ├── test_real_server.py   # Real server tests
│   └── ...                   # Other test files
│
├── run_client.py             # Main entry point
├── demo.py                   # Demo script
└── README.md                 # This file
```

## 🚀 Cách sử dụng

### 1. Command Line Interface (CLI)
```bash
# Default mode
python run_client.py

# Explicit CLI mode
python run_client.py --cli
```

### 2. Graphical User Interface (GUI)
```bash
python run_client.py --gui
```

### 3. Demo
```bash
python demo.py
```

## ⚡ Tính năng chính

- ✅ **Raw Socket Implementation**: Không dùng ftplib, chỉ socket thô
- ✅ **Passive & Active Mode**: Hỗ trợ cả hai chế độ FTP
- ✅ **Binary & ASCII Transfer**: Upload/Download cả hai kiểu
- ✅ **Directory Operations**: mkdir, rmdir, ls, cd
- ✅ **File Operations**: get, put, delete, rename, mget, mput
- ✅ **Virus Scanning**: Tích hợp ClamAV để quét virus
- ✅ **GUI & CLI**: Cả giao diện đồ họa và dòng lệnh
- ✅ **Error Handling**: Xử lý đầy đủ FTP error codes
- ✅ **Modular Structure**: Tổ chức code rõ ràng, dễ maintain

## 🔧 Kiến trúc Raw Socket

### Core Components (`client/core/`)

#### `raw_socket_ftp.py`
- Raw socket functions: `ftp_connect()`, `ftp_login()`, `ftp_send_command()`
- FTP protocol implementation từ đầu
- Wrapper class `FTP` để tương thích

#### `ftp_command.py`
- Command line interface
- 26+ FTP commands: ls, cd, get, put, mkdir, etc.
- Interactive shell

#### `ftp_helpers.py`
- Upload/Download utilities
- Progress tracking
- File transfer helpers

### UI Components (`client/ui/`)

#### `ftp_gui.py`
- Main GUI application
- File browser interface
- Progress bars, status updates

#### `login_window.py`
- Login dialog
- Connection management

### Networking (`client/networking/`)

#### `client.py`
- Network client utilities
- Connection management

## 🧪 Testing

```bash
# Run all tests
cd ftp_project
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_real_server.py -v

# Demo imports
python demo.py
```

## 📚 Giao thức FTP được implement

- **Control Connection**: Port 21, command/response
- **Data Connection**: Dynamic ports, file transfer  
- **Commands**: USER, PASS, PWD, CWD, MKD, RMD, DELE, RNFR, RNTO, SIZE, NLST, LIST, RETR, STOR, PASV, PORT, QUIT
- **Response Codes**: 1xx, 2xx, 3xx, 4xx, 5xx parsing
- **Transfer Modes**: Binary (TYPE I), ASCII (TYPE A)

## 🎯 Lợi ích của cấu trúc mới

1. **Separation of Concerns**: Core logic tách biệt với UI
2. **Modular Design**: Dễ maintain và extend
3. **Clean Architecture**: Rõ ràng, dễ hiểu
4. **Testability**: Dễ test từng component
5. **Scalability**: Dễ thêm tính năng mới

## 🚀 Kết luận

Project này cung cấp một FTP client hoàn chỉnh **KHÔNG SỬ DỤNG FTPLIB**, được implement hoàn toàn bằng raw socket với cấu trúc code chuyên nghiệp và dễ maintain.
