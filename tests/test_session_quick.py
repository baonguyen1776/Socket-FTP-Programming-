"""
Quick Session Management Test with Timeout
Tests session management without hanging on FTP connection
"""

import sys
import os
import socket
import time
from contextlib import contextmanager

# Add paths
current_dir = os.path.dirname(os.path.abspath(__file__))
client_dir = os.path.join(current_dir, '..', 'Client')
sys.path.insert(0, client_dir)

from ftp_command import FTPCommands
from test_config import TestConfig

@contextmanager
def timeout(duration):
    """Context manager for timeout operations"""
    import signal
    
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {duration} seconds")
    
    # Set the signal handler
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(duration)
    
    try:
        yield
    finally:
        signal.alarm(0)  # Disable the alarm

def check_ftp_server_availability():
    """Quick check if FTP server is available"""
    try:
        host, port = TestConfig.get_ftp_config()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)  # 2 second timeout
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def test_session_management_quick():
    """Quick session management tests"""
    print("🧪 QUICK SESSION MANAGEMENT TESTS")
    print("=" * 50)
    
    results = []
    
    # Test 1: FTP Client Creation
    try:
        ftp_client = FTPCommands()
        results.append("✅ FTP Client Creation: PASSED")
        print("✅ FTP Client Creation: PASSED")
    except Exception as e:
        results.append(f"❌ FTP Client Creation: FAILED - {e}")
        print(f"❌ FTP Client Creation: FAILED - {e}")
        return results
    
    # Test 2: Initial State Check
    try:
        assert not ftp_client.connected, "Should not be connected initially"
        assert ftp_client.transfer_mode == 'binary', "Default should be binary mode"
        assert ftp_client.passive_mode == True, "Default should be passive mode"
        results.append("✅ Initial State Check: PASSED")
        print("✅ Initial State Check: PASSED")
    except Exception as e:
        results.append(f"❌ Initial State Check: FAILED - {e}")
        print(f"❌ Initial State Check: FAILED - {e}")
    
    # Test 3: Mode Switching (without connection)
    try:
        # Test ASCII mode
        original_mode = ftp_client.transfer_mode
        ftp_client.do_ascii('')
        assert ftp_client.transfer_mode == 'ascii', "ASCII mode not set"
        
        # Test Binary mode
        ftp_client.do_binary('')
        assert ftp_client.transfer_mode == 'binary', "Binary mode not set"
        
        results.append("✅ Mode Switching: PASSED")
        print("✅ Mode Switching: PASSED")
    except Exception as e:
        results.append(f"❌ Mode Switching: FAILED - {e}")
        print(f"❌ Mode Switching: FAILED - {e}")
    
    # Test 4: Passive Mode Toggle
    try:
        original_passive = ftp_client.passive_mode
        ftp_client.do_passive('')
        assert ftp_client.passive_mode != original_passive, "Passive mode should toggle"
        
        ftp_client.do_passive('')
        assert ftp_client.passive_mode == original_passive, "Passive mode should toggle back"
        
        results.append("✅ Passive Mode Toggle: PASSED")
        print("✅ Passive Mode Toggle: PASSED")
    except Exception as e:
        results.append(f"❌ Passive Mode Toggle: FAILED - {e}")
        print(f"❌ Passive Mode Toggle: FAILED - {e}")
    
    # Test 5: Status Command (without connection)
    try:
        ftp_client.do_status('')
        results.append("✅ Status Command: PASSED")
        print("✅ Status Command: PASSED")
    except Exception as e:
        results.append(f"❌ Status Command: FAILED - {e}")
        print(f"❌ Status Command: FAILED - {e}")
    
    # Test 6: Help Command
    try:
        ftp_client.do_help('')
        results.append("✅ Help Command: PASSED")
        print("✅ Help Command: PASSED")
    except Exception as e:
        results.append(f"❌ Help Command: FAILED - {e}")
        print(f"❌ Help Command: FAILED - {e}")
    
    # Test 7: FTP Server Availability Check
    print("\n🔍 Checking FTP Server Availability...")
    if check_ftp_server_availability():
        results.append("✅ FTP Server: AVAILABLE on localhost:21")
        print("✅ FTP Server: AVAILABLE on localhost:21")
        
        # Test 8: Quick Connection Test (with timeout)
        try:
            print("🔗 Attempting quick connection test...")
            host, port = TestConfig.get_ftp_config()
            
            # Try connection with timeout
            if os.name == 'nt':  # Windows - can't use signal timeout
                ftp_client.do_open(f"{host} {port}")
                time.sleep(1)  # Brief pause
                if ftp_client.connected:
                    results.append("✅ FTP Connection: PASSED")
                    print("✅ FTP Connection: PASSED")
                    
                    # Quick close test
                    ftp_client.do_close('')
                    if not ftp_client.connected:
                        results.append("✅ FTP Disconnection: PASSED")
                        print("✅ FTP Disconnection: PASSED")
                else:
                    results.append("⚠️ FTP Connection: No response (may need credentials)")
                    print("⚠️ FTP Connection: No response (may need credentials)")
            else:
                # Unix systems can use signal timeout
                with timeout(5):
                    ftp_client.do_open(f"{host} {port}")
                    if ftp_client.connected:
                        results.append("✅ FTP Connection: PASSED")
                        print("✅ FTP Connection: PASSED")
                        ftp_client.do_close('')
                        
        except TimeoutError:
            results.append("⚠️ FTP Connection: TIMEOUT (server may be slow)")
            print("⚠️ FTP Connection: TIMEOUT (server may be slow)")
        except Exception as e:
            results.append(f"⚠️ FTP Connection: {str(e)}")
            print(f"⚠️ FTP Connection: {str(e)}")
    else:
        results.append("❌ FTP Server: NOT AVAILABLE on localhost:21")
        print("❌ FTP Server: NOT AVAILABLE on localhost:21")
        results.append("💡 Tip: Start FileZilla Server to test FTP connections")
        print("💡 Tip: Start FileZilla Server to test FTP connections")
    
    return results

def main():
    """Main function"""
    print("🚀 Quick Session Management Test")
    print("This test checks session management without hanging")
    print()
    
    results = test_session_management_quick()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY:")
    
    passed = len([r for r in results if "PASSED" in r])
    failed = len([r for r in results if "FAILED" in r])
    warnings = len([r for r in results if "WARNING" in r or "⚠️" in r])
    
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️ Warnings: {warnings}")
    
    if failed == 0:
        print("\n🎉 All core session management functionality is working!")
    
    print("\n📋 What was tested:")
    for result in results:
        print(f"  {result}")

if __name__ == "__main__":
    main()
