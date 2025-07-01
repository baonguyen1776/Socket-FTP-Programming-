"""
Test Runner for FTP Client
Modern test runner with clean interface
"""

import os
import sys
import subprocess
import json
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
        print("\n" + "="*50)
        print("FTP CLIENT TEST SUITE")
        print("="*50)
        print("1. Session Tests (OPEN, CLOSE, STATUS)")
        print("2. File Tests (GET, PUT, MGET, MPUT)")
        print("3. Directory Tests (LS, CD, MKDIR, RMDIR)")
        print("4. Local Tests (LCD)")
        print("5. All Tests")
        print("6. Server Check")
        print("7. Generate Report")
        print("0. Exit")
        print()
        
    def get_user_choice(self):
        """Lấy lựa chọn từ người dùng với validation"""
        while True:
            try:
                choice = input("Enter your choice (0-7): ").strip()
                if choice in ['0', '1', '2', '3', '4', '5', '6', '7']:
                    return choice
                else:
                    print("Invalid choice. Please enter 0-7.")
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
    
    def run_session_tests(self):
        """Chạy test session management"""
        print("Running Session Tests")
        
        # Set up credentials for interactive tests
        self._setup_credentials_if_needed()
        
        args = ["test_session.py", "-v", "--tb=short"]
        return self.run_pytest_command(args)
    
    def run_file_tests(self):
        """Chạy test file operations"""
        print("Running File Operation Tests")
        
        # Set up credentials for interactive tests
        self._setup_credentials_if_needed()
        
        args = ["test_file.py", "-v", "--tb=short"]
        return self.run_pytest_command(args)
    
    def _setup_credentials_if_needed(self):
        """Check FTP credentials for integration tests"""
        import os
        if not os.getenv('FTP_TEST_USER') or not os.getenv('FTP_TEST_PASS'):
            print("\n⚠ WARNING: FTP credentials not found!")
            print("Please set environment variables:")
            print("  $env:FTP_TEST_USER=\"your_username\"")
            print("  $env:FTP_TEST_PASS=\"your_password\"")
            print("Some tests may fail without proper credentials.\n")
    
    def run_directory_tests(self):
        """Chạy test directory operations"""
        print("Running Directory Tests")
        args = ["test_directory.py", "-v", "--tb=short"]
        return self.run_pytest_command(args)
    
    def run_local_tests(self):
        """Chạy test local operations"""
        print("Running Local Tests")
        args = ["test_local.py", "-v", "--tb=short"]
        return self.run_pytest_command(args)
    
    def run_all_tests(self):
        """Run all tests including slow ones"""
        print("Running ALL Tests (May take a while)")
        args = [
            "-v",
            "--tb=short",
            "--durations=10"
        ]
        return self.run_pytest_command(args)
    
    def generate_text_report(self):
        """Tạo báo cáo text đơn giản"""
        print("Generating Text Report")
        report_dir = self.tests_dir / "reports"
        report_dir.mkdir(exist_ok=True)
        
        # Chạy pytest và lưu output vào file
        report_file = report_dir / "test_report.txt"
        
        args = [
            "-v",
            "--tb=short",
            "--durations=10"
        ]
        
        cmd = [sys.executable, "-m", "pytest"] + args
        
        try:
            # Chạy pytest và capture output
            result = subprocess.run(
                cmd, 
                cwd=self.tests_dir, 
                capture_output=True, 
                text=True
            )
            
            # Tạo báo cáo text
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("="*60 + "\n")
                f.write("FTP CLIENT TEST REPORT\n")
                f.write("="*60 + "\n")
                f.write(f"Generated: {timestamp}\n\n")
                
                f.write("PYTEST OUTPUT:\n")
                f.write("-" * 40 + "\n")
                f.write(result.stdout)
                
                if result.stderr:
                    f.write("\n\nERRORS:\n")
                    f.write("-" * 40 + "\n")
                    f.write(result.stderr)
                
                f.write(f"\n\nEXIT CODE: {result.returncode}\n")
                f.write("="*60 + "\n")
            
            print(f"Report generated: {report_file}")
            return result.returncode == 0
            
        except Exception as e:
            print(f"Error generating report: {e}")
            return False
    
    def check_servers(self):
        """Check server availability"""
        print("Checking Server Availability")
        print("-" * 30)
        
        import socket
        
        # Check FTP
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(("127.0.0.1", 21))
            sock.close()
            
            if result == 0:
                print("FTP Server: Available at 127.0.0.1:21")
            else:
                print("FTP Server: Not available at 127.0.0.1:21")
        except Exception as e:
            print(f"FTP Server: Check failed - {e}")
        
        # Check ClamAV
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(("127.0.0.1", 9001))
            sock.close()
            
            if result == 0:
                print("ClamAV Server: Available at 127.0.0.1:9001")
            else:
                print("ClamAV Server: Not available at 127.0.0.1:9001")
        except Exception as e:
            print(f"ClamAV Server: Check failed - {e}")
    
    def run(self):
        """Vòng lặp menu chính"""
        print("Welcome to FTP Client Test Suite")
        print("Modern test runner with better features and reporting!")
        
        while True:
            self.display_menu()
            choice = self.get_user_choice()
            
            success = True
            if choice == '0':
                print("Goodbye!")
                break
            elif choice == '1':
                success = self.run_session_tests()
            elif choice == '2':
                success = self.run_file_tests()
            elif choice == '3':
                success = self.run_directory_tests()
            elif choice == '4':
                success = self.run_local_tests()
            elif choice == '5':
                success = self.run_all_tests()
            elif choice == '6':
                self.check_servers()
            elif choice == '7':
                success = self.generate_text_report()
            
            if choice in ['1', '2', '3', '4', '5', '7']:
                if success:
                    print("\nTests completed successfully!")
                else:
                    print("\nSome tests failed or encountered errors.")
            
            if choice != '0':
                input("\nPress Enter to continue...")


def main():
    """Điểm khởi đầu chính"""
    # Kiểm tra pytest có sẵn không
    try:
        import pytest
        print("pytest is available")
    except ImportError:
        print("pytest not found!")
        print("Please install requirements: pip install -r requirements.txt")
        sys.exit(1)
    
    # Prompt for credentials at startup for integration tests
    print("\nNote: Some tests require FTP server credentials.")
    print("You can set FTP_TEST_USER and FTP_TEST_PASS environment variables")
    print("or enter them when prompted during tests.\n")
    
    runner = FTPTestRunner()
    runner.run()


if __name__ == '__main__':
    main()
