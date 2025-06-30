"""
Fixed FTP Client Test Runner with Better Error Handling
This script provides a robust menu-driven interface to run various test suites for the FTP client.
"""

import os
import sys
import unittest
import datetime
from io import StringIO
import json
import time
import signal

# Add parent directory to path to import test modules and client modules
current_dir = os.path.dirname(os.path.abspath(__file__))
client_dir = os.path.join(current_dir, '..', 'Client')
sys.path.insert(0, client_dir)
sys.path.insert(0, current_dir)

from test_config import TestConfig

# Quick server availability check
def quick_server_check():
    """Quick check if FTP server is available"""
    try:
        import socket
        host, port = TestConfig.get_ftp_config()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)  # Very short timeout
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            print(f"✅ FTP Server detected at {host}:{port}")
            return True
        else:
            print(f"❌ FTP Server not available at {host}:{port}")
            return False
    except Exception as e:
        print(f"❌ FTP Server check failed: {str(e)}")
        return False

class TimeoutHandler:
    """Handle timeouts for long-running operations"""
    def __init__(self, timeout_seconds=30):
        self.timeout_seconds = timeout_seconds
        self.timed_out = False
    
    def timeout_handler(self, signum, frame):
        self.timed_out = True
        raise TimeoutError(f"Operation timed out after {self.timeout_seconds} seconds")
    
    def __enter__(self):
        if hasattr(signal, 'SIGALRM'):  # Unix/Linux only
            signal.signal(signal.SIGALRM, self.timeout_handler)
            signal.alarm(self.timeout_seconds)
        return self
    
    def __exit__(self, type, value, traceback):
        if hasattr(signal, 'SIGALRM'):
            signal.alarm(0)

class TestRunner:
    """Main test runner class with menu interface"""
    
    def __init__(self):
        self.results_file = TestConfig.TEST_RESULTS_FILE
        self.all_results = []
        
    def display_menu(self):
        """Display the main test menu"""
        print("\n" + "="*60)
        print("FTP CLIENT TEST SUITE - FIXED VERSION")
        print("="*60)
        print("Select which tests to run:")
        print()
        print("1. Quick File Operations Tests (Mock/Safe)")
        print("2. Quick Directory Operations Tests (Mock/Safe)")
        print("3. Real FTP Server Tests (Requires FTP Server)")
        print("4. Local Operations Tests (No Server Required)")
        print("5. Configuration Tests")
        print("6. Server Availability Check")
        print("7. View Test Configuration")
        print("8. View Last Test Results")
        print("9. Clear Test Results")
        print("0. Exit")
        print()
        
    def get_user_choice(self):
        """Get user menu choice"""
        while True:
            try:
                choice = input("Enter your choice (0-9): ").strip()
                if choice in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                    return choice
                else:
                    print("Invalid choice. Please enter a number between 0-9.")
            except KeyboardInterrupt:
                print("\nExiting...")
                sys.exit(0)
            except Exception:
                print("Invalid input. Please try again.")
    
    def run_quick_file_ops_test(self):
        """Run quick file operations test without hanging"""
        print(f"\n{'='*50}")
        print("RUNNING QUICK FILE OPERATIONS TEST")
        print(f"{'='*50}")
        
        try:
            # Import the quick test
            import quick_file_ops_test
            
            # Run the quick test
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromModule(quick_file_ops_test)
            
            # Create output capture
            output = StringIO()
            runner = unittest.TextTestRunner(stream=output, verbosity=2)
            
            print("Running quick file operations tests...")
            start_time = time.time()
            
            result = runner.run(suite)
            
            end_time = time.time()
            test_output = output.getvalue()
            
            print(test_output)
            print(f"\nTest completed in {end_time - start_time:.2f} seconds")
            print(f"Tests Run: {result.testsRun}")
            print(f"Failures: {len(result.failures)}")
            print(f"Errors: {len(result.errors)}")
            
            # Save results
            summary = {
                'suite_name': 'Quick File Operations',
                'timestamp': datetime.datetime.now().isoformat(),
                'tests_run': result.testsRun,
                'failures': len(result.failures),
                'errors': len(result.errors),
                'duration': end_time - start_time,
                'output': test_output
            }
            self.all_results.append(summary)
            
        except ImportError:
            print("❌ Quick file operations test not found. Creating it now...")
            self.create_quick_file_test()
        except Exception as e:
            print(f"❌ Error running quick file operations test: {str(e)}")
    
    def run_quick_dir_ops_test(self):
        """Run quick directory operations test"""
        print(f"\n{'='*50}")
        print("RUNNING QUICK DIRECTORY OPERATIONS TEST")
        print(f"{'='*50}")
        
        # Simple directory operations test
        tests_run = 0
        failures = 0
        
        try:
            # Test basic imports
            print("✅ Testing imports...")
            sys.path.insert(0, os.path.join(current_dir, '..', 'Client'))
            from ftp_command import FTPCommands
            tests_run += 1
            
            print("✅ Testing FTPCommands initialization...")
            ftp_client = FTPCommands()
            tests_run += 1
            
            print("✅ Testing local directory commands...")
            # Test LCD (local change directory)
            import tempfile
            temp_dir = tempfile.mkdtemp()
            old_cwd = os.getcwd()
            ftp_client.do_lcd(temp_dir)
            tests_run += 1
            
            # Clean up
            os.chdir(old_cwd)
            os.rmdir(temp_dir)
            
            print(f"\n✅ Quick directory operations test completed!")
            print(f"Tests Run: {tests_run}")
            print(f"Failures: {failures}")
            
        except Exception as e:
            failures += 1
            print(f"❌ Error in directory operations test: {str(e)}")
    
    def run_real_ftp_tests(self):
        """Run real FTP server tests with proper checks"""
        print(f"\n{'='*50}")
        print("RUNNING REAL FTP SERVER TESTS")
        print(f"{'='*50}")
        
        # Check if server is available first
        if not quick_server_check():
            print("\n❌ FTP Server is not available!")
            print("Please start your FTP server (e.g., FileZilla Server) on localhost:21")
            print("and try again.")
            return
        
        try:
            # Try to import and run real tests with timeout
            with TimeoutHandler(30):  # 30 second timeout
                import test_file_operations
                
                loader = unittest.TestLoader()
                suite = loader.loadTestsFromModule(test_file_operations)
                
                output = StringIO()
                runner = unittest.TextTestRunner(stream=output, verbosity=2)
                
                print("Running real FTP tests (timeout: 30s)...")
                result = runner.run(suite)
                
                test_output = output.getvalue()
                print(test_output)
                
                print(f"Tests Run: {result.testsRun}")
                print(f"Failures: {len(result.failures)}")
                print(f"Errors: {len(result.errors)}")
                
        except TimeoutError:
            print("❌ Tests timed out! FTP server may be unresponsive.")
        except Exception as e:
            print(f"❌ Error running real FTP tests: {str(e)}")
    
    def run_local_tests(self):
        """Run tests that don't require FTP server"""
        print(f"\n{'='*50}")
        print("RUNNING LOCAL OPERATIONS TESTS")
        print(f"{'='*50}")
        
        try:
            import test_local_operations
            
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromModule(test_local_operations)
            
            output = StringIO()
            runner = unittest.TextTestRunner(stream=output, verbosity=2)
            
            result = runner.run(suite)
            
            test_output = output.getvalue()
            print(test_output)
            
            print(f"Tests Run: {result.testsRun}")
            print(f"Failures: {len(result.failures)}")
            print(f"Errors: {len(result.errors)}")
            
        except Exception as e:
            print(f"❌ Error running local tests: {str(e)}")
    
    def run_config_tests(self):
        """Test configuration and setup"""
        print(f"\n{'='*50}")
        print("RUNNING CONFIGURATION TESTS")
        print(f"{'='*50}")
        
        tests_run = 0
        failures = 0
        
        try:
            # Test config import
            print("✅ Testing config import...")
            from test_config import TestConfig
            tests_run += 1
            
            # Test config values
            print("✅ Testing config values...")
            host, port = TestConfig.get_ftp_config()
            username, password = TestConfig.get_credentials()
            
            print(f"  FTP Host: {host}")
            print(f"  FTP Port: {port}")
            print(f"  Username: {username}")
            print(f"  Password: {'*' * len(password)}")
            tests_run += 1
            
            # Test test data directory
            print("✅ Testing test data directory...")
            if os.path.exists(TestConfig.TEST_DATA_DIR):
                print(f"  Test data dir exists: {TestConfig.TEST_DATA_DIR}")
                files = os.listdir(TestConfig.TEST_DATA_DIR)
                print(f"  Files found: {files}")
            else:
                print(f"  ❌ Test data dir missing: {TestConfig.TEST_DATA_DIR}")
                failures += 1
            tests_run += 1
            
            print(f"\n✅ Configuration tests completed!")
            print(f"Tests Run: {tests_run}")
            print(f"Failures: {failures}")
            
        except Exception as e:
            failures += 1
            print(f"❌ Configuration test error: {str(e)}")
    
    def check_server_availability(self):
        """Check FTP and ClamAV server availability"""
        print(f"\n{'='*50}")
        print("CHECKING SERVER AVAILABILITY")
        print(f"{'='*50}")
        
        # Check FTP server
        print("Checking FTP Server...")
        ftp_available = quick_server_check()
        
        # Check ClamAV server
        print("\nChecking ClamAV Server...")
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((TestConfig.CLAMAV_HOST, TestConfig.CLAMAV_PORT))
            sock.close()
            if result == 0:
                print(f"✅ ClamAV Server detected at {TestConfig.CLAMAV_HOST}:{TestConfig.CLAMAV_PORT}")
                clamav_available = True
            else:
                print(f"❌ ClamAV Server not available at {TestConfig.CLAMAV_HOST}:{TestConfig.CLAMAV_PORT}")
                clamav_available = False
        except Exception as e:
            print(f"❌ ClamAV Server check failed: {str(e)}")
            clamav_available = False
        
        print(f"\n{'='*30}")
        print("SERVER AVAILABILITY SUMMARY")
        print(f"{'='*30}")
        print(f"FTP Server: {'✅ Available' if ftp_available else '❌ Not Available'}")
        print(f"ClamAV Server: {'✅ Available' if clamav_available else '❌ Not Available'}")
        
        if not ftp_available:
            print("\n📝 To start FTP Server:")
            print("  - Install FileZilla Server")
            print("  - Configure user 'test' with password 'test123'")
            print("  - Start server on localhost:21")
        
        if not clamav_available:
            print("\n📝 To start ClamAV Server:")
            print("  - Run: python ClamAvAgent/sever_clam.py")
            print("  - Server should start on localhost:9001")
    
    def view_test_configuration(self):
        """Display current test configuration"""
        print(f"\n{'='*50}")
        print("CURRENT TEST CONFIGURATION")
        print(f"{'='*50}")
        
        try:
            from test_config import TestConfig
            
            host, port = TestConfig.get_ftp_config()
            username, password = TestConfig.get_credentials()
            
            print(f"FTP Server: {host}:{port}")
            print(f"FTP Username: {username}")
            print(f"FTP Password: {'*' * len(password)}")
            print(f"ClamAV Host: {TestConfig.CLAMAV_HOST}")
            print(f"ClamAV Port: {TestConfig.CLAMAV_PORT}")
            print(f"Test Data Directory: {TestConfig.TEST_DATA_DIR}")
            print(f"Results File: {TestConfig.TEST_RESULTS_FILE}")
            print(f"FTP Timeout: {TestConfig.FTP_TIMEOUT}s")
            print(f"ClamAV Timeout: {TestConfig.CLAMAV_TIMEOUT}s")
            
            # Check if test data files exist
            print(f"\nTest Data Files:")
            test_files = [
                TestConfig.SMALL_TEXT_FILE,
                TestConfig.LARGE_TEXT_FILE,
                TestConfig.VIRUS_TEST_FILE
            ]
            
            for filename in test_files:
                filepath = os.path.join(TestConfig.TEST_DATA_DIR, filename)
                status = "✅ Found" if os.path.exists(filepath) else "❌ Missing"
                print(f"  {filename}: {status}")
                
        except Exception as e:
            print(f"❌ Error loading configuration: {str(e)}")
    
    def view_last_results(self):
        """View the last test results"""
        print(f"\n{'='*50}")
        print("LAST TEST RESULTS")
        print(f"{'='*50}")
        
        if self.all_results:
            for result in self.all_results[-3:]:  # Show last 3 results
                print(f"\nSuite: {result.get('suite_name', 'Unknown')}")
                print(f"Time: {result.get('timestamp', 'Unknown')}")
                print(f"Tests: {result.get('tests_run', 0)}")
                print(f"Failures: {result.get('failures', 0)}")
                print(f"Errors: {result.get('errors', 0)}")
                if 'duration' in result:
                    print(f"Duration: {result['duration']:.2f}s")
        else:
            print("No test results available yet.")
    
    def clear_results(self):
        """Clear all test results"""
        self.all_results = []
        if os.path.exists(self.results_file):
            os.remove(self.results_file)
        print("✅ Test results cleared.")
    
    def create_quick_file_test(self):
        """Create a quick file test if it doesn't exist"""
        quick_test_content = '''"""
Quick file operations test without FTP server dependency
"""
import unittest
import os
import sys

# Add client directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
client_dir = os.path.join(current_dir, '..', 'Client')
sys.path.insert(0, client_dir)

class QuickFileTest(unittest.TestCase):
    
    def test_imports(self):
        """Test that we can import FTP modules"""
        try:
            from ftp_command import FTPCommands
            self.assertTrue(True, "FTPCommands imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import FTPCommands: {e}")
    
    def test_ftp_initialization(self):
        """Test FTP client initialization"""
        try:
            from ftp_command import FTPCommands
            client = FTPCommands()
            self.assertIsNotNone(client, "FTP client created successfully")
        except Exception as e:
            self.fail(f"Failed to create FTP client: {e}")

if __name__ == '__main__':
    unittest.main()
'''
        
        with open(os.path.join(current_dir, 'quick_file_ops_test.py'), 'w') as f:
            f.write(quick_test_content)
        print("✅ Created quick_file_ops_test.py")
    
    def run(self):
        """Main menu loop"""
        while True:
            self.display_menu()
            choice = self.get_user_choice()
            
            if choice == '0':
                print("Goodbye!")
                break
            elif choice == '1':
                self.run_quick_file_ops_test()
            elif choice == '2':
                self.run_quick_dir_ops_test()
            elif choice == '3':
                self.run_real_ftp_tests()
            elif choice == '4':
                self.run_local_tests()
            elif choice == '5':
                self.run_config_tests()
            elif choice == '6':
                self.check_server_availability()
            elif choice == '7':
                self.view_test_configuration()
            elif choice == '8':
                self.view_last_results()
            elif choice == '9':
                self.clear_results()
            
            input("\nPress Enter to continue...")


def main():
    """Main entry point"""
    print("FTP Client Test Suite - Fixed Version")
    print("This version includes better error handling and timeouts")
    
    runner = TestRunner()
    runner.run()


if __name__ == '__main__':
    main()
