# FTP Client Test Suite - Complete Guide

Comprehensive testing framework for FTP client with real server integration.

## Files Structure

```
tests/
├── test_runner.py                    # Interactive test runner (menu-driven)
├── test_real_server.py              # Core FTP functionality tests
├── test_ftp_navigation.py           # Directory navigation tests
├── test_ftp_transfer_mode.py        # Active/passive mode tests
├── test_ftp_local_operations.py     # Local command tests (lcd, lpwd,lls)
├── test_ftp_multiple_operations.py  # Multiple file operations (mput, mget)
├── test_config.py                   # Test configuration settings
├── conftest.py                      # Test fixtures and cleanup utilities
├── pytest.ini                      # Pytest configuration
└── reports/                         # Test reports directory (auto-created)
```

## Quick Start

**Prerequisites:**
- Python 3.8+ with pytest installed (`pip install pytest`)
- Real FTP server running on localhost:21 (for integration tests)
- ClamAV virus scanner on localhost:9001 (optional, tests use mock by default)

**Essential Setup:**

```powershell
# Step 1: Set FTP credentials (REQUIRED for all tests)
$env:FTP_TEST_USER="your_username"
$env:FTP_TEST_PASS="your_password"

# Step 2: Navigate to tests directory
cd tests

# Step 3: Run tests using interactive menu (RECOMMENDED)
python test_runner.py
```

**Alternative Command Line Options:**

```powershell
# Run all test files
pytest -v

# Run specific test categories
pytest test_real_server.py -v              # Core FTP functionality
pytest test_ftp_navigation.py -v           # Directory operations
pytest test_ftp_multiple_operations.py -v  # Multiple file operations
pytest test_ftp_local_operations.py -v     # Local commands
pytest test_ftp_transfer_mode.py -v        # Transfer modes

# Generate detailed report
pytest --tb=short --durations=10
```

## Test Configuration

All tests are **Real Server Integration Tests** - no mock tests are used.

**Environment Variables (REQUIRED):**
```powershell
$env:FTP_TEST_USER="your_username"      # FTP username
$env:FTP_TEST_PASS="your_password"      # FTP password
```

**Server Settings** (edit `test_config.py` if needed):
```python
FTP_HOST = '127.0.0.1'          # FTP server address
FTP_PORT = 21                   # FTP server port
CLAMAV_HOST = '127.0.0.1'       # ClamAV virus scanner
CLAMAV_PORT = 9001              # ClamAV port
```

## Interactive Test Runner Features

The `test_runner.py` provides a comprehensive menu-driven interface:

**Menu Options:**
1. **Run All FTP Server Tests** - Complete test suite
2. **Connection Tests** - Basic connectivity and commands
3. **File Operations Tests** - Upload, download, delete, rename
4. **Directory Operations Tests** - Directory management  
5. **Extended Functionality Tests** - Advanced features
6. **Server Availability Check** - Check FTP/ClamAV servers
7. **Generate Complete Test Report** - Detailed test report
8. **Cleanup Temporary Files** - Remove test artifacts

**Key Features:**
- ✅ Automatic cleanup of test files and directories
- ✅ Real-time server availability checking
- ✅ Comprehensive test reports with timestamps
- ✅ Error handling and recovery
- ✅ English output, Vietnamese code comments

## Utility Tools

**cleanup.py** (Personal workspace tool):
- Removes empty files and temporary files
- Cleans up test artifacts
- Maintains workspace hygiene
- Usage: `python cleanup.py` (manual cleanup)

## Common Issues & Solutions

**❌ "FTP credentials not found!" Error:**
```powershell
# Solution: Set environment variables
$env:FTP_TEST_USER="your_username"
$env:FTP_TEST_PASS="your_password"
```

**❌ "pytest: reading from stdin while output is captured!":**
- **Fixed**: Tests now run without stdin issues
- Prompts are automatically disabled in test environment

**❌ "PermissionError: [WinError 32] The process cannot access the file":**
- **Fixed**: Improved temp file cleanup on Windows
- Tests now handle file locks gracefully

**❌ Connection timeouts or failures:**
- Check FTP server is running on 127.0.0.1:21
- Verify firewall settings allow FTP connections
- Test with: `python test_runner.py` → Option 6 (Server Availability Check)

**❌ Import errors:**
- Ensure you're in the `tests/` directory: `cd tests`
- Check Python path includes the Client directory

**❌ ClamAV errors:**
- ClamAV server is optional for most tests
- Tests use mock virus scanner by default
- Start ClamAV server if you need real virus scanning
