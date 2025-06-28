# Hướng dẫn chạy pytest cho dự án FTP Socket Programming

## 📊 Tóm tắt Tests
- **Tổng số tests**: 29 tests
- **Status**: ✅ All tests passing  
- **Modules được test**: Client (15 tests) + ClamAV Agent (14 tests)
- **Coverage**: FTP commands, virus scanning, server operations, error handling

## Cài đặt dependencies

```bash
pip install -r requirements-test.txt
```

## Chạy tất cả tests

```bash
# Chạy tất cả tests (29 tests)
pytest

# Chạy với coverage report
pytest --cov=Client --cov=ClamAvAgent

# Chạy với output verbose
pytest -v

# Chạy với thời gian thực thi
pytest --durations=10
```

## Chạy tests theo category

```bash
# Chỉ unit tests
pytest -m unit

# Chỉ integration tests  
pytest -m integration

# Chạy tests cho Client module
pytest tests/client/

# Chạy tests cho ClamAV Agent
pytest tests/clamav_agent/
```

## Chạy test cụ thể

```bash
# Chạy một test file
pytest tests/client/test_virus_scan.py

# Chạy một test class
pytest tests/client/test_ftp_command.py::TestFTPCommands

# Chạy một test method
pytest tests/client/test_virus_scan.py::TestVirusScan::test_scan_file_clean
```

## Test Coverage

```bash
# Tạo coverage report
pytest --cov=Client --cov=ClamAvAgent --cov-report=html

# Xem coverage report trong browser
open htmlcov/index.html
```

## Cấu trúc Tests

- `tests/client/` - Tests cho FTP client components (15 tests)
  - `test_virus_scan.py` - 6 tests: file scanning, error handling, timeouts
  - `test_ftp_command.py` - 9 tests: connection, commands, error scenarios
- `tests/clamav_agent/` - Tests cho ClamAV agent components (14 tests)
  - `test_scanner.py` - 7 tests: file scanning, large files, error handling
  - `test_server_clam.py` - 7 tests: server initialization, binding, connections
- `tests/fixtures/` - Test data và helper files
- `conftest.py` - Pytest fixtures và configuration

## Lưu ý quan trọng

1. **Mock external dependencies**: Tất cả network calls, file operations được mock
2. **Isolated tests**: Mỗi test độc lập, không phụ thuộc vào test khác
3. **Test data cleanup**: Temporary files được cleanup sau mỗi test
4. **Error scenarios**: Test cả success và failure cases
5. **Fast execution**: 29 tests chạy trong ~0.12 giây

## Ví dụ chạy tests

```bash
# Development workflow
pytest tests/client/test_virus_scan.py -v

# Before commit
pytest --cov=Client --cov=ClamAvAgent --cov-fail-under=80

# CI/CD pipeline
pytest --junitxml=test-results.xml --cov=Client --cov=ClamAvAgent --cov-report=xml
```

## 📋 Test Results Summary

### Client Module Tests (15 tests)
```
tests/client/test_virus_scan.py::TestVirusScan::test_initialization ✅
tests/client/test_virus_scan.py::TestVirusScan::test_scan_file_clean ✅
tests/client/test_virus_scan.py::TestVirusScan::test_scan_file_not_found ✅
tests/client/test_virus_scan.py::TestVirusScan::test_scan_directory_instead_of_file ✅
tests/client/test_virus_scan.py::TestVirusScan::test_scan_file_virus_detected ✅
tests/client/test_virus_scan.py::TestVirusScan::test_scan_file_connection_error ✅
tests/client/test_virus_scan.py::TestVirusScan::test_scan_file_timeout ✅

tests/client/test_ftp_command.py::TestFTPCommands::test_initialization ✅
tests/client/test_ftp_command.py::TestFTPCommands::test_do_open_basic ✅
tests/client/test_ftp_command.py::TestFTPCommands::test_commands_without_connection ✅
tests/client/test_ftp_command.py::TestFTPCommands::test_do_ls_with_connection ✅
tests/client/test_ftp_command.py::TestFTPCommands::test_do_cd_success ✅
tests/client/test_ftp_command.py::TestFTPCommands::test_do_pwd ✅
tests/client/test_ftp_command.py::TestFTPCommands::test_passive_mode_toggle ✅
tests/client/test_ftp_command.py::TestFTPCommands::test_ftp_cmd_error_handling ✅
tests/client/test_ftp_command.py::TestFTPCommands::test_precmd_logging ✅
```

### ClamAV Agent Tests (14 tests)
```
tests/clamav_agent/test_scanner.py::TestClamAVScanner::test_initialization ✅
tests/clamav_agent/test_scanner.py::TestClamAVScanner::test_scan_clean_file ✅
tests/clamav_agent/test_scanner.py::TestClamAVScanner::test_scan_infected_file ✅
tests/clamav_agent/test_scanner.py::TestClamAVScanner::test_scan_nonexistent_file ✅
tests/clamav_agent/test_scanner.py::TestClamAVScanner::test_scan_scanner_error ✅
tests/clamav_agent/test_scanner.py::TestClamAVScanner::test_scan_timeout ✅
tests/clamav_agent/test_scanner.py::TestClamAVScanner::test_scan_large_file ✅

tests/clamav_agent/test_server_clam.py::TestClamAVAgentServer::test_initialization ✅
tests/clamav_agent/test_server_clam.py::TestClamAVAgentServer::test_temp_directory_creation ✅
tests/clamav_agent/test_server_clam.py::TestClamAVAgentServer::test_server_start_and_bind ✅
tests/clamav_agent/test_server_clam.py::TestClamAVAgentServer::test_simple_client_handling ✅
tests/clamav_agent/test_server_clam.py::TestClamAVAgentServer::test_server_socket_timeout_handling ✅
tests/clamav_agent/test_server_clam.py::TestClamAVAgentServer::test_server_stop ✅
tests/clamav_agent/test_server_clam.py::TestClamAVAgentServer::test_server_error_handling ✅
```

## 🛠️ Troubleshooting

### Nếu gặp lỗi import module:
```bash
# Đảm bảo đang ở đúng thư mục
cd "Socket-FTP-Programming-"

# Chạy từ root directory
python -m pytest tests/
```

### Nếu tests chạy chậm:
```bash
# Chạy parallel (nếu có pytest-xdist)
pytest -n auto tests/

# Chạy chỉ failed tests
pytest --lf tests/
```

### Kiểm tra test coverage:
```bash
# Coverage report chi tiết
pytest --cov=Client --cov=ClamAvAgent --cov-report=term-missing

# Export coverage report
pytest --cov=Client --cov=ClamAvAgent --cov-report=html
```

### Nếu gặp lỗi "ERROR collecting debug_test.py":
```bash
# Xóa file debug hoặc các file test cũ ở root directory
Remove-Item "debug_test.py" -Force

# Xóa cache files
Remove-Item "__pycache__" -Recurse -Force
Remove-Item ".pytest_cache" -Recurse -Force

# Chạy lại pytest
pytest
```

### Chỉ chạy tests trong thư mục tests/:
```bash
# Specify exact test directory để tránh collect files khác
pytest tests/
```
