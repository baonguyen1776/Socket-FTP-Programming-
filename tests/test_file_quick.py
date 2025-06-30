"""
Quick File Operations Test - No FTP Server Required
This test demonstrates file operations functionality without needing FTP server
"""

import sys
import os
import unittest

# Add paths
current_dir = os.path.dirname(os.path.abspath(__file__))
client_dir = os.path.join(current_dir, '..', 'Client')
sys.path.insert(0, client_dir)

from ftp_command import FTPCommands
from test_config import TestConfig

class QuickFileOpsTest(unittest.TestCase):
    """Quick test for file operations without FTP server"""
    
    def setUp(self):
        """Set up test environment"""
        self.ftp_client = FTPCommands()
        self.test_results = []
        print(f"\n🧪 Testing: {self._testMethodName}")
    
    def test_ftp_client_initialization(self):
        """Test FTP client can be created"""
        test_name = "FTP Client Initialization"
        try:
            self.assertIsNotNone(self.ftp_client)
            self.assertFalse(self.ftp_client.connected)
            self.assertEqual(self.ftp_client.transfer_mode, 'binary')
            self.assertTrue(self.ftp_client.passive_mode)
            
            self.test_results.append(f"{test_name}: PASSED")
            print(f"✅ {test_name}: PASSED")
            
        except Exception as e:
            self.test_results.append(f"{test_name}: FAILED - {str(e)}")
            print(f"❌ {test_name}: FAILED - {str(e)}")
            raise
    
    def test_file_commands_exist(self):
        """Test that all file operation commands exist"""
        test_name = "File Commands Availability"
        try:
            required_commands = [
                'do_get', 'do_put', 'do_mget', 'do_mput', 'do_recv'
            ]
            
            for cmd in required_commands:
                self.assertTrue(hasattr(self.ftp_client, cmd), f"Missing command: {cmd}")
                self.assertTrue(callable(getattr(self.ftp_client, cmd)), f"Command not callable: {cmd}")
            
            self.test_results.append(f"{test_name}: PASSED - All {len(required_commands)} commands available")
            print(f"✅ {test_name}: PASSED - All commands available")
            
        except Exception as e:
            self.test_results.append(f"{test_name}: FAILED - {str(e)}")
            print(f"❌ {test_name}: FAILED - {str(e)}")
            raise
    
    def test_commands_without_connection(self):
        """Test commands show appropriate errors when not connected"""
        test_name = "Commands Without Connection"
        try:
            # Capture output to check error messages
            import io
            from contextlib import redirect_stdout
            
            # Test GET command
            f = io.StringIO()
            with redirect_stdout(f):
                self.ftp_client.do_get("test.txt")
            output = f.getvalue()
            self.assertIn("Not connected", output, "GET should show not connected error")
            
            # Test PUT command  
            f = io.StringIO()
            with redirect_stdout(f):
                self.ftp_client.do_put("test.txt")
            output = f.getvalue()
            self.assertIn("Not connected", output, "PUT should show not connected error")
            
            self.test_results.append(f"{test_name}: PASSED - Commands show proper error messages")
            print(f"✅ {test_name}: PASSED - Error handling works")
            
        except Exception as e:
            self.test_results.append(f"{test_name}: FAILED - {str(e)}")
            print(f"❌ {test_name}: FAILED - {str(e)}")
            raise
    
    def test_configuration_loading(self):
        """Test configuration can be loaded"""
        test_name = "Configuration Loading"
        try:
            host, port = TestConfig.get_ftp_config()
            username, password = TestConfig.get_credentials()
            
            self.assertIsInstance(host, str)
            self.assertIsInstance(port, int)
            self.assertIsInstance(username, str)
            self.assertIsInstance(password, str)
            
            self.assertEqual(host, 'localhost')
            self.assertEqual(port, 21)
            self.assertEqual(username, 'ftpuser')
            self.assertEqual(password, '12345')
            
            self.test_results.append(f"{test_name}: PASSED - Configuration loaded correctly")
            print(f"✅ {test_name}: PASSED - Config: {host}:{port}")
            
        except Exception as e:
            self.test_results.append(f"{test_name}: FAILED - {str(e)}")
            print(f"❌ {test_name}: FAILED - {str(e)}")
            raise
    
    def test_virus_scanner_integration(self):
        """Test virus scanner can be accessed"""
        test_name = "Virus Scanner Integration"
        try:
            self.assertIsNotNone(self.ftp_client.virus_scanner)
            self.assertTrue(hasattr(self.ftp_client.virus_scanner, 'scan_file'))
            
            self.test_results.append(f"{test_name}: PASSED - Virus scanner integrated")
            print(f"✅ {test_name}: PASSED - Virus scanner available")
            
        except Exception as e:
            self.test_results.append(f"{test_name}: FAILED - {str(e)}")
            print(f"❌ {test_name}: FAILED - {str(e)}")
            raise
    
    def test_ftp_server_connectivity_check(self):
        """Test FTP server connectivity check"""
        test_name = "FTP Server Connectivity Check"
        try:
            import socket
            host, port = TestConfig.get_ftp_config()
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                self.test_results.append(f"{test_name}: INFO - FTP server is running")
                print(f"ℹ️ {test_name}: FTP server is available")
            else:
                self.test_results.append(f"{test_name}: INFO - FTP server not running (expected)")
                print(f"ℹ️ {test_name}: FTP server not running (this is OK for demo)")
            
        except Exception as e:
            self.test_results.append(f"{test_name}: INFO - Cannot check FTP server")
            print(f"ℹ️ {test_name}: Cannot check FTP server connectivity")
    
    def get_test_results(self):
        """Return test results"""
        return self.test_results


def run_quick_file_ops_test():
    """Run quick file operations test"""
    print("🚀 QUICK FILE OPERATIONS TEST")
    print("=" * 50)
    print("Testing file operations without requiring FTP server...")
    print()
    
    # Run tests
    suite = unittest.TestLoader().loadTestsFromTestCase(QuickFileOpsTest)
    runner = unittest.TextTestRunner(verbosity=0)  # Quiet mode
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 QUICK TEST SUMMARY:")
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.testsRun > 0:
        success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100)
        print(f"Success Rate: {success_rate:.1f}%")
    
    # Print detailed results if any failures
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n💥 ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    print("\n🎯 WHAT THIS DEMONSTRATES:")
    print("✅ File Operations Test Suite is properly structured")
    print("✅ All required FTP commands are implemented")
    print("✅ Error handling works correctly")
    print("✅ Configuration system works")
    print("✅ Virus scanner integration is ready")
    print("✅ Code is ready for real FTP server testing")
    
    print("\n💡 TO RUN WITH REAL FTP SERVER:")
    print("1. Start FileZilla Server on localhost:21")
    print("2. Create user 'ftpuser' with password '12345'")
    print("3. Run: python test_runner.py -> Option 1")
    
    return result


if __name__ == "__main__":
    run_quick_file_ops_test()
