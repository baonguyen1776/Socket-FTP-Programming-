"""
Test Runner for FTP Client
Modern test runner with clean interface
"""

import os
import sys
import subprocess
from pathlib import Path
import datetime


class FTPTestRunner:
    """Test runner với giao diện menu"""
    
    def __init__(self):
        # Khởi tạo đường dẫn thư mục
        self.tests_dir = Path(__file__).parent
        self.root_dir = self.tests_dir.parent
        
    def display_menu(self):
        """Hiển thị menu chính"""
        print("\n" + "="*70)
        print("FTP CLIENT TEST SUITE")
        print("REAL SERVER INTEGRATION TESTS ONLY")
        print("="*70)
        print("1. Run All FTP Server Tests")
        print("2. Connection Tests (open, close, status, pwd)")
        print("3. File Operations Tests (put, get, delete, rename)")
        print("4. Directory Operations Tests (mkdir, rmdir, cd, ls)")
        print("5. Extended Functionality Tests:")
        print("   • Transfer Modes (passive/active mode switching)")
        print("   • Local Operations (lcd, lpwd, lls commands)")
        print("   • Multiple Files (mput, mget with wildcards)")
        print("6. Server Availability Check")
        print("7. Generate Complete Test Report")
        print("8. Cleanup Temporary Files")
        print("0. Exit")
        print()
        print("      Test Functions Coverage:")
        print("   • Basic: open, close, status, pwd, ls")
        print("   • Files: put, get, delete, rename")
        print("   • Dirs: mkdir, rmdir, cd, cdup")
        print("   • Local: lcd, lpwd, lls")
        print("   • Multi: mput, mget")
        print("   • Modes: passive, active")
        print()
        print("       All tests require real FTP server credentials")
        print("   Set: $env:FTP_TEST_USER and $env:FTP_TEST_PASS")
        print()
        
    def get_user_choice(self):
        """Lấy lựa chọn từ người dùng với validation"""
        while True:
            try:
                choice = input("Enter your choice (0-8): ").strip()
                if choice in ['0', '1', '2', '3', '4', '5', '6', '7', '8']:
                    return choice
                else:
                    print("Invalid choice. Please enter 0-8.")
            except KeyboardInterrupt:
                print("\nGoodbye!")
                sys.exit(0)
    
    def run_pytest_command(self, args):
        """Chạy pytest với các tham số được cung cấp"""
        cmd = [sys.executable, "-m", "pytest"] + args
        print(f"Running: {' '.join(cmd)}")
        print("-" * 50)
        
        try:
            result = subprocess.run(cmd, cwd=self.tests_dir, capture_output=False)
            return result.returncode == 0
        except Exception as e:
            print(f"Error running pytest: {e}")
            return False
    
    def _setup_credentials_if_needed(self):
        """Kiểm tra FTP credentials cho real server tests - BẮT BUỘC"""
        if not os.getenv('FTP_TEST_USER') or not os.getenv('FTP_TEST_PASS'):
            print("\n  ERROR: FTP credentials not found!")
            print("Real server tests REQUIRE credentials to be set.")
            print("Please set environment variables:")
            print("  $env:FTP_TEST_USER=\"your_username\"")
            print("  $env:FTP_TEST_PASS=\"your_password\"")
            print("\nAll tests require a real FTP server connection.")
            print("No mock or unit tests are available.\n")
            return False
        return True
    
    def run_real_server_tests(self):
        """Chạy comprehensive real server tests - tất cả chức năng"""
        print("  Running COMPREHENSIVE REAL SERVER Tests")
        print("    Testing all FTP functionality with actual server...")
        
        # Require credentials for all tests
        if not self._setup_credentials_if_needed():
            return False
        
        print("\n--- Running Core FTP Tests (open, close, status, pwd) ---")
        args = [
            "test_real_server.py",
            "-v", 
            "--tb=short",
            "-m", "real_server"
        ]
        result1 = self.run_pytest_command(args)
        
        print("\n--- Running Directory Navigation Tests (cd, ls, mkdir, rmdir) ---")
        args2 = ["test_ftp_navigation.py", "-v", "--tb=short"]
        result2 = self.run_pytest_command(args2)
        
        print("\n--- Running Transfer Mode Tests (passive/active modes) ---")
        args3 = ["test_ftp_transfer_mode.py", "-v", "--tb=short"]
        result3 = self.run_pytest_command(args3)
        
        print("\n--- Running Local Operations Tests (lcd, lpwd, lls) ---")
        args4 = ["test_ftp_local_operations.py", "-v", "--tb=short"]
        result4 = self.run_pytest_command(args4)
        
        print("\n--- Running Multiple File Operations Tests (mput, mget) ---")
        args5 = ["test_ftp_multiple_operations.py", "-v", "--tb=short"]
        result5 = self.run_pytest_command(args5)
        
        return result1 and result2 and result3 and result4 and result5
    
    def auto_cleanup(self):
        """Tự động dọn dẹp các file trống và temporary"""
        try:
            from cleanup import cleanup_empty_files, cleanup_temp_files
            print("  Running automatic cleanup...")
            empty_files = cleanup_empty_files(self.tests_dir)
            temp_files = cleanup_temp_files(self.tests_dir)
            total = len(empty_files) + len(temp_files)
            if total > 0:
                print(f"   Cleaned up {total} unwanted files.")
            else:
                print("  No cleanup needed - workspace is clean.")
        except Exception as e:
            print(f" Auto cleanup failed: {e}")
    
    def manual_cleanup(self):
        """Trigger dọn dẹp thủ công cho người dùng"""
        print(" Running Manual Cleanup...")
        print("    Removing empty files and temporary files...")
        
        try:
            from cleanup import cleanup_empty_files, cleanup_temp_files
            empty_files = cleanup_empty_files(self.tests_dir)
            temp_files = cleanup_temp_files(self.tests_dir)
            
            print(f"\n  Cleanup Results:")
            print(f"   • Empty files removed: {len(empty_files)}")
            print(f"   • Temp files removed: {len(temp_files)}")
            print(f"   • Total files cleaned: {len(empty_files) + len(temp_files)}")
            
            if empty_files:
                print(f"\n   Empty files removed:")
                for f in empty_files[:5]:  # Show max 5
                    print(f"   - {f}")
                if len(empty_files) > 5:
                    print(f"   ... and {len(empty_files) - 5} more")
            
            if temp_files:
                print(f"\n   Temp files removed:")
                for f in temp_files[:5]:  # Show max 5
                    print(f"   - {f}")
                if len(temp_files) > 5:
                    print(f"   ... and {len(temp_files) - 5} more")
            
            if not empty_files and not temp_files:
                print("  Workspace is already clean!")
                
            return True
            
        except Exception as e:
            print(f"  Manual cleanup failed: {e}")
            return False
    
    def generate_text_report(self):
        """Tạo báo cáo"""
        print("  Generating Comprehensive Test Report...")
        report_dir = self.tests_dir / "reports"
        report_dir.mkdir(exist_ok=True)
        
        # Check credentials first
        if not self._setup_credentials_if_needed():
            print("  Cannot generate report without FTP credentials.")
            return False
        
        # Run pytest and save output to file
        report_file = report_dir / "ftp_integration_test_report.txt"
        
        # List all test files to run
        test_files = [
            "test_real_server.py",
            "test_ftp_navigation.py",
            "test_ftp_transfer_mode.py",
            "test_ftp_local_operations.py",
            "test_ftp_multiple_operations.py"
        ]
        
        args = [
            *test_files,
            "-v",
            "--tb=short",
            "--durations=10"
        ]
        
        cmd = [sys.executable, "-m", "pytest"] + args
        
        try:
            # Run pytest and capture output
            result = subprocess.run(
                cmd, 
                cwd=self.tests_dir, 
                capture_output=True, 
                text=True
            )
            
            # Create comprehensive text report
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("="*80 + "\n")
                f.write("FTP CLIENT INTEGRATION TEST REPORT\n")
                f.write("REAL SERVER TESTS - FULL FUNCTIONALITY COVERAGE\n")
                f.write("="*80 + "\n")
                f.write(f"Generated: {timestamp}\n")
                f.write("Test Environment: Real FTP Server Integration Tests\n\n")
                
                f.write("  TESTED FUNCTIONALITY:\n")
                f.write("-" * 40 + "\n")
                f.write("• Connection: open, close, status, pwd\n")
                f.write("• File Operations: put, get, delete, rename\n")
                f.write("• Directory Operations: mkdir, rmdir, cd, ls, cdup\n")
                f.write("• Local Operations: lcd, lpwd, lls\n")
                f.write("• Multiple Files: mput, mget (with wildcards)\n")
                f.write("• Transfer Modes: passive, active mode switching\n")
                f.write("• Server Capabilities: FEAT, SYST commands\n\n")
                
                f.write("PYTEST EXECUTION OUTPUT:\n")
                f.write("-" * 40 + "\n")
                f.write(result.stdout)
                
                if result.stderr:
                    f.write("\n\nERROR OUTPUT:\n")
                    f.write("-" * 40 + "\n")
                    f.write(result.stderr)
                
                f.write(f"\n\nEXIT CODE: {result.returncode}\n")
                f.write("SUCCESS" if result.returncode == 0 else "SOME TESTS FAILED")
                f.write("\n" + "="*80 + "\n")
            
            print(f"  Report generated: {report_file}")
            return result.returncode == 0
            
        except Exception as e:
            print(f"Error generating report: {e}")
            return False
    
    def check_servers(self):
        """Kiểm tra tình trạng server và khả năng kết nối"""
        print("  Checking Server Availability")
        print("-" * 40)
        
        import socket
        
        # Check FTP Server
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(("127.0.0.1", 21))
            sock.close()
            
            if result == 0:
                print("  FTP Server: Available at 127.0.0.1:21")
            else:
                print("  FTP Server: Not available at 127.0.0.1:21")
        except Exception as e:
            print(f"  FTP Server: Check failed - {e}")
        
        # Check ClamAV Server
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(("127.0.0.1", 9001))
            sock.close()
            
            if result == 0:
                print("  ClamAV Server: Available at 127.0.0.1:9001")
            else:
                print("  ClamAV Server: Not available at 127.0.0.1:9001")
        except Exception as e:
            print(f"  ClamAV Server: Check failed - {e}")
        
        # Check environment variables
        if os.getenv('FTP_TEST_USER') and os.getenv('FTP_TEST_PASS'):
            print("  FTP Credentials: Environment variables set")
        else:
            print("  FTP Credentials: Environment variables NOT set")
    
    def run_connection_tests(self):
        """Chạy các test kết nối FTP và lệnh cơ bản"""
        print("🔌 Running CONNECTION & BASIC COMMAND Tests")
        print("    Testing: open, close, status, pwd, ls commands...")
        
        # Require credentials for all tests
        if not self._setup_credentials_if_needed():
            return False
        
        print("   Functions being tested:")
        print("   • open - Connect to FTP server")
        print("   • close - Disconnect from server") 
        print("   • status - Check connection status")
        print("   • pwd - Print working directory")
        print("   • ls - List directory contents")
        
        args = [
            "test_real_server.py",
            "-v", 
            "--tb=short",
            "-k", "test_connection"
        ]
        return self.run_pytest_command(args)
    
    def run_file_tests(self):
        """Chạy các test thao tác file"""
        print("   Running FILE OPERATION Tests")
        print("    Testing: put, get, delete, rename operations...")
        
        # Require credentials for all tests
        if not self._setup_credentials_if_needed():
            return False
        
        print("  Functions being tested:")
        print("   • put - Upload files to server")
        print("   • get - Download files from server")
        print("   • delete - Remove files from server")
        print("   • rename - Rename files on server")
        print("   • File integrity validation")
        
        args = [
            "test_real_server.py",
            "-v", 
            "--tb=short",
            "-k", "test_file"
        ]
        return self.run_pytest_command(args)
    
    def run_directory_tests(self):
        """Chạy các test thao tác thư mục"""
        print("  Running DIRECTORY OPERATION Tests")
        print("    Testing: mkdir, rmdir, cd, ls, cdup operations...")
        
        # Require credentials for all tests
        if not self._setup_credentials_if_needed():
            return False
        
        print("  Functions being tested:")
        print("   • mkdir - Create directories")
        print("   • rmdir - Remove directories") 
        print("   • cd - Change directory")
        print("   • ls - List directory contents")
        print("   • cdup - Change to parent directory")
        print("   • pwd - Print working directory")
        
        # Run directory tests from test_real_server.py
        args1 = [
            "test_real_server.py",
            "-v", 
            "--tb=short",
            "-k", "test_directory"
        ]
        
        result1 = self.run_pytest_command(args1)
        
        # Run specialized navigation tests
        args2 = [
            "test_ftp_navigation.py",
            "-v", 
            "--tb=short"
        ]
        
        print("\n--- Running Advanced Directory Navigation Tests ---")
        result2 = self.run_pytest_command(args2)
        
        return result1 and result2
    
    def run_extended_tests(self):
        """Chạy các test chức năng mở rộng"""
        print("  Running EXTENDED FUNCTIONALITY Tests")
        print("    Testing: transfer modes, local ops, multiple files...")
        
        # Require credentials for all tests
        if not self._setup_credentials_if_needed():
            return False
        
        print("\n--- Running Server Capabilities Tests ---")
        print("  Functions: FEAT, SYST, server info")
        args = [
            "test_real_server.py",
            "-v", 
            "--tb=short",
            "-k", "test_listing or test_server"
        ]
        result1 = self.run_pytest_command(args)
        
        print("\n--- Running Transfer Mode Tests ---")
        print("  Functions: passive mode, active mode switching")
        args2 = [
            "test_ftp_transfer_mode.py", 
            "-v", 
            "--tb=short"
        ]
        result2 = self.run_pytest_command(args2)
        
        print("\n--- Running Local Operations Tests ---")
        print("  Functions: lcd, lpwd, lls (local commands)")
        args3 = [
            "test_ftp_local_operations.py",
            "-v",
            "--tb=short"
        ]
        result3 = self.run_pytest_command(args3)
        
        print("\n--- Running Multiple File Operations Tests ---")
        print("  Functions: mput, mget (with wildcards)")
        args4 = [
            "test_ftp_multiple_operations.py",
            "-v",
            "--tb=short"
        ]
        result4 = self.run_pytest_command(args4)
        
        return result1 and result2 and result3 and result4
    
    def run(self):
        """Vòng lặp menu chính cho real server tests"""
        print("  Welcome to FTP Client Test Suite")
        print("REAL SERVER INTEGRATION TESTS - Complete FTP functionality testing!")
        
        # Auto cleanup on startup
        self.auto_cleanup()
        
        while True:
            self.display_menu()
            choice = self.get_user_choice()
            success = True
            if choice == '0':
                print("  Goodbye!")
                break
            elif choice == '1':
                success = self.run_real_server_tests()
            elif choice == '2':
                success = self.run_connection_tests()
            elif choice == '3':
                success = self.run_file_tests()
            elif choice == '4':
                success = self.run_directory_tests()
            elif choice == '5':
                success = self.run_extended_tests()
            elif choice == '6':
                self.check_servers()
            elif choice == '7':
                success = self.generate_text_report()
            elif choice == '8':
                success = self.manual_cleanup()
            if choice in ['1', '2', '3', '4', '5', '7']:
                if success:
                    print("\n  Tests completed successfully!")
                else:
                    print("\n  Some tests failed or encountered errors.")
            if choice != '0':
                input("\nPress Enter to continue...")


def main():
    """Điểm khởi đầu chính"""
    # Check if pytest is available
    try:
        import pytest
        print("  pytest is available")
    except ImportError:
        print("  pytest not found!")
        print("Please install requirements: pip install -r requirements.txt")
        sys.exit(1)
    
    # Information about test requirements
    print("\n  FTP Integration Test Suite")
    print("This suite tests ALL FTP client functionality:")
    print("• Connection management (open, close, status)")
    print("• File operations (put, get, delete, rename)")
    print("• Directory operations (mkdir, rmdir, cd, ls)")
    print("• Local operations (lcd, lpwd, lls)")
    print("• Multiple file operations (mput, mget)")
    print("• Transfer modes (passive, active)")
    print("• Server capabilities (FEAT, SYST)")
    print("\n   All tests require FTP server credentials.")
    print("Set environment variables: FTP_TEST_USER and FTP_TEST_PASS\n")
    
    runner = FTPTestRunner()
    runner.run()


if __name__ == '__main__':
    main()
