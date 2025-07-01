# Test Suite - How to Run

Quick guide for running FTP client tests.

## Files Structure

```
tests/
├── test_runner.py          # Interactive test runner
├── test_session.py         # Session tests (OPEN, CLOSE, STATUS)
├── test_file.py            # File tests (GET, PUT, MGET, MPUT)
├── test_directory.py       # Directory tests (LS, CD, MKDIR, RMDIR)
├── test_local.py           # Local tests (LCD)
├── conftest.py             # Test setup and fixtures
├── pytest.ini             # Test configuration
└── test_data/              # Test files
```

## Quick Start

**Prerequisites:**
- Python with pytest installed
- FTP server running on localhost:21 (for integration tests)
- ClamAV server on localhost:9001 (for virus tests)

**Run Tests:**

```bash
# Step 1: Set FTP credentials (REQUIRED)
$env:FTP_TEST_USER="your_username"
$env:FTP_TEST_PASS="your_password"

# Step 2: Run tests
pytest                    # All tests
pytest -m session         # Session tests only
pytest -m file_ops         # File operation tests only
python test_runner.py      # Interactive menu
```

## Test Configuration

Edit `test_config.py` for FTP server settings:
```python
FTP_HOST = 'localhost'
FTP_PORT = 21
# Credentials must be set via environment variables
FTP_USERNAME = None  
FTP_PASSWORD = None
```

**Required Environment Variables:**
```bash
$env:FTP_TEST_USER="your_username"
$env:FTP_TEST_PASS="your_password"

## Common Issues

- **Connection Failed**: Check FTP server is running
- **Import Errors**: Run from tests directory: `cd tests`
- **Permission Errors**: Ensure FTP user has write access
- Ensure tests clean up properly

Happy Testing!
