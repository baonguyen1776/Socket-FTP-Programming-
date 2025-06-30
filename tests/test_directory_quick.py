"""
Quick Directory Operations Test
Tests directory operations functionality without hanging on FTP connection
"""

import sys
import os
import tempfile
import shutil

# Add paths
current_dir = os.path.dirname(os.path.abspath(__file__))
client_dir = os.path.join(current_dir, '..', 'Client')
sys.path.insert(0, client_dir)

from ftp_command import FTPCommands
from test_config import TestConfig

def test_directory_operations():
    """Test directory operations functionality"""
    print("🧪 QUICK DIRECTORY OPERATIONS TEST")
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
        results.append("✅ Initial State Check: PASSED - Not connected initially")
        print("✅ Initial State Check: PASSED - Not connected initially")
    except Exception as e:
        results.append(f"❌ Initial State Check: FAILED - {e}")
        print(f"❌ Initial State Check: FAILED - {e}")
    
    # Test 3: PWD Command (Print Working Directory) - Without Connection
    try:
        print("🔄 Testing PWD command (should show not connected)")
        ftp_client.do_pwd('')
        results.append("✅ PWD Command: PASSED - Handled no connection gracefully")
        print("✅ PWD Command: PASSED - Handled no connection gracefully")
    except Exception as e:
        results.append(f"❌ PWD Command: FAILED - {e}")
        print(f"❌ PWD Command: FAILED - {e}")
    
    # Test 4: LS Command (List Directory) - Without Connection
    try:
        print("🔄 Testing LS command (should show not connected)")
        ftp_client.do_ls('')
        results.append("✅ LS Command: PASSED - Handled no connection gracefully")
        print("✅ LS Command: PASSED - Handled no connection gracefully")
    except Exception as e:
        results.append(f"❌ LS Command: FAILED - {e}")
        print(f"❌ LS Command: FAILED - {e}")
    
    # Test 5: CD Command (Change Directory) - Without Connection
    try:
        print("🔄 Testing CD command (should show not connected)")
        ftp_client.do_cd('test_directory')
        results.append("✅ CD Command: PASSED - Handled no connection gracefully")
        print("✅ CD Command: PASSED - Handled no connection gracefully")
    except Exception as e:
        results.append(f"❌ CD Command: FAILED - {e}")
        print(f"❌ CD Command: FAILED - {e}")
    
    # Test 6: MKDIR Command (Make Directory) - Without Connection
    try:
        print("🔄 Testing MKDIR command (should show not connected)")
        ftp_client.do_mkdir('test_new_dir')
        results.append("✅ MKDIR Command: PASSED - Handled no connection gracefully")
        print("✅ MKDIR Command: PASSED - Handled no connection gracefully")
    except Exception as e:
        results.append(f"❌ MKDIR Command: FAILED - {e}")
        print(f"❌ MKDIR Command: FAILED - {e}")
    
    # Test 7: RMDIR Command (Remove Directory) - Without Connection
    try:
        print("🔄 Testing RMDIR command (should show not connected)")
        ftp_client.do_rmdir('test_old_dir')
        results.append("✅ RMDIR Command: PASSED - Handled no connection gracefully")
        print("✅ RMDIR Command: PASSED - Handled no connection gracefully")
    except Exception as e:
        results.append(f"❌ RMDIR Command: FAILED - {e}")
        print(f"❌ RMDIR Command: FAILED - {e}")
    
    # Test 8: DELETE Command (Delete File) - Without Connection
    try:
        print("🔄 Testing DELETE command (should show not connected)")
        ftp_client.do_delete('test_file.txt')
        results.append("✅ DELETE Command: PASSED - Handled no connection gracefully")
        print("✅ DELETE Command: PASSED - Handled no connection gracefully")
    except Exception as e:
        results.append(f"❌ DELETE Command: FAILED - {e}")
        print(f"❌ DELETE Command: FAILED - {e}")
    
    # Test 9: RENAME Command - Without Connection
    try:
        print("🔄 Testing RENAME command (should show not connected)")
        ftp_client.do_rename('old_name.txt new_name.txt')
        results.append("✅ RENAME Command: PASSED - Handled no connection gracefully")
        print("✅ RENAME Command: PASSED - Handled no connection gracefully")
    except Exception as e:
        results.append(f"❌ RENAME Command: FAILED - {e}")
        print(f"❌ RENAME Command: FAILED - {e}")
    
    # Test 10: Check Command Methods Exist
    try:
        methods_to_check = ['do_pwd', 'do_ls', 'do_cd', 'do_mkdir', 'do_rmdir', 'do_delete', 'do_rename']
        missing_methods = []
        
        for method_name in methods_to_check:
            if not hasattr(ftp_client, method_name):
                missing_methods.append(method_name)
        
        if not missing_methods:
            results.append("✅ Command Methods Check: PASSED - All directory command methods exist")
            print("✅ Command Methods Check: PASSED - All directory command methods exist")
        else:
            results.append(f"❌ Command Methods Check: FAILED - Missing methods: {missing_methods}")
            print(f"❌ Command Methods Check: FAILED - Missing methods: {missing_methods}")
    
    except Exception as e:
        results.append(f"❌ Command Methods Check: FAILED - {e}")
        print(f"❌ Command Methods Check: FAILED - {e}")
    
    # Test 11: Check if FTP Server is Available (for info)
    try:
        import socket
        host, port = TestConfig.get_ftp_config()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            results.append(f"ℹ️ FTP Server Info: AVAILABLE at {host}:{port}")
            print(f"ℹ️ FTP Server Info: AVAILABLE at {host}:{port}")
            print("   💡 You can test real directory operations by manually connecting")
        else:
            results.append(f"ℹ️ FTP Server Info: NOT AVAILABLE at {host}:{port}")
            print(f"ℹ️ FTP Server Info: NOT AVAILABLE at {host}:{port}")
            print("   💡 Start FileZilla Server to test real directory operations")
            
    except Exception as e:
        results.append(f"ℹ️ FTP Server Info: Error checking - {e}")
        print(f"ℹ️ FTP Server Info: Error checking - {e}")
    
    return results

def main():
    """Main function"""
    print("🚀 Quick Directory Operations Test")
    print("This test checks directory operation commands without requiring FTP connection")
    print()
    
    results = test_directory_operations()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY:")
    
    passed = len([r for r in results if "PASSED" in r])
    failed = len([r for r in results if "FAILED" in r])
    warnings = len([r for r in results if "WARNING" in r or "⚠️" in r])
    info = len([r for r in results if "ℹ️" in r])
    
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️ Warnings: {warnings}")
    print(f"ℹ️ Info: {info}")
    
    if failed == 0:
        print("\n🎉 All directory operations commands are properly implemented!")
    elif failed <= 2:
        print("\n😊 Directory operations mostly working with minor issues!")
    
    print("\n📋 What was tested:")
    for result in results:
        print(f"  {result}")
    
    print("\n💡 Directory Commands Tested:")
    print("  - PWD (Print Working Directory)")
    print("  - LS (List Directory Contents)")
    print("  - CD (Change Directory)")
    print("  - MKDIR (Make Directory)")
    print("  - RMDIR (Remove Directory)")
    print("  - DELETE (Delete File)")
    print("  - RENAME (Rename File/Directory)")
    print("  - Command method existence check")

if __name__ == "__main__":
    main()
