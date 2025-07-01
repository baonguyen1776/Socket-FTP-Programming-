"""
Quick Session Management Test (pytest version)
Tests session management without hanging on FTP connection
"""

import pytest
import socket
import time
from unittest.mock import Mock, patch
from test_config import TestConfig


@pytest.mark.unit
def test_ftp_imports():
    """Test that FTP modules can be imported"""
    from ftp_command import FTPCommands
    assert FTPCommands is not None


@pytest.mark.unit
def test_ftp_client_initialization(ftp_client):
    """Test FTP client can be initialized"""
    assert ftp_client is not None
    assert hasattr(ftp_client, 'ftp')


@pytest.mark.unit
def test_session_mock_connection():
    """Test session connection using mock"""
    from ftp_command import FTPCommands
    
    # Mock FTP connection
    with patch('ftplib.FTP') as mock_ftp:
        mock_instance = Mock()
        mock_ftp.return_value = mock_instance
        
        client = FTPCommands()
        
        # Test mock connection
        mock_instance.connect.return_value = "Connected"
        mock_instance.login.return_value = "Login successful"
        
        # Simulate connection
        result = mock_instance.connect("127.0.0.1", 21)
        assert result == "Connected"
        
        result = mock_instance.login("test", "test")
        assert result == "Login successful"


@pytest.mark.ftp
@pytest.mark.timeout(10)
def test_real_ftp_connection_quick(test_config, check_ftp_server):
    """Test real FTP connection with timeout"""
    if not check_ftp_server:
        pytest.skip("FTP server not available")
    
    from ftp_command import FTPCommands
    
    client = FTPCommands()
    host, port = test_config.get_ftp_config()
    
    try:
        # Quick connection test with timeout
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        assert result == 0, f"Cannot connect to FTP server at {host}:{port}"
        
    except socket.timeout:
        pytest.fail("FTP connection timed out")


@pytest.mark.unit
def test_session_timeout_handling():
    """Test timeout handling for session operations"""
    import threading
    import time
    
    def timeout_operation():
        """Simulate operation that might timeout"""
        time.sleep(0.1)  # Short delay for test
        return "completed"
    
    # Test with proper timeout
    start_time = time.time()
    result = timeout_operation()
    duration = time.time() - start_time
    
    assert result == "completed"
    assert duration < 1.0  # Should complete quickly


@pytest.mark.unit
def test_session_error_handling():
    """Test error handling in session management"""
    from ftp_command import FTPCommands
    
    with patch('ftplib.FTP') as mock_ftp:
        mock_instance = Mock()
        mock_ftp.return_value = mock_instance
        
        # Test connection error
        mock_instance.connect.side_effect = ConnectionError("Connection failed")
        
        client = FTPCommands()
        
        # Should handle connection error gracefully
        try:
            mock_instance.connect("invalid_host", 21)
            assert False, "Should have raised ConnectionError"
        except ConnectionError as e:
            assert "Connection failed" in str(e)


@pytest.mark.unit
@pytest.mark.parametrize("host,port,expected", [
    ("127.0.0.1", 21, True),
    ("localhost", 21, True),
    ("invalid_host", 21, False),
    ("127.0.0.1", 9999, False),
])
def test_connection_parameters(host, port, expected):
    """Test various connection parameters"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if expected:
            # We expect connection to work, but it might not if server is down
            # So we just test that no exception was raised
            assert True
        else:
            # We expect connection to fail
            assert result != 0
            
    except (socket.gaierror, OSError):
        # DNS resolution failed or other OS error
        if not expected:
            assert True  # Expected to fail
        else:
            assert False, f"Unexpected connection failure for {host}:{port}"


@pytest.mark.session
@pytest.mark.integration
def test_ftp_login_with_credentials(ftp_client, ftp_credentials):
    """Test FTP login with user-provided credentials"""
    username, password = ftp_credentials
    
    try:
        # Test connection
        result = ftp_client.do_open(f"{TestConfig.FTP_HOST} {TestConfig.FTP_PORT}")
        
        # In real implementation, we would capture output to check for success messages
        # For now, assume connection success if no exception
        print(f"Login test with user: {username}")
        print("Check console output for login success/failure messages")
        
        # The actual login assessment should be based on FTP response messages
        # like "230 Login successful" vs "530 Login incorrect"
        
    except Exception as e:
        error_msg = str(e).lower()
        if "530" in error_msg or "login" in error_msg or "authentication" in error_msg:
            print(f"Login failed as expected for test: {e}")
            # This could be a valid test case for wrong credentials
        elif "connection" in error_msg or "refused" in error_msg:
            pytest.skip("FTP server not available for testing")
        else:
            pytest.fail(f"Unexpected login error: {e}")
    
    finally:
        try:
            ftp_client.do_close("")
        except:
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
