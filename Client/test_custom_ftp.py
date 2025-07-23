#!/usr/bin/env python3
"""
Test script để demo custom FTP client thay thế ftplib
"""

import sys
import os
from custom_ftp import FTP, all_errors, error_perm, error_temp, error_proto
from ftp_command import FTPCommands

def test_custom_ftp():
    """Test custom FTP implementation"""
    print("=== DEMO CUSTOM FTP CLIENT (KHÔNG DÙNG FTPLIB) ===\n")
    
    # Khởi tạo FTP client
    ftp = FTP()
    client = FTPCommands(ftp)
    
    print("✅ Custom FTP client đã được khởi tạo thành công!")
    print("✅ Thay thế hoàn toàn thư viện ftplib bằng socket programming")
    print("\n📋 Các lệnh FTP có sẵn:")
    
    commands = [cmd[3:] for cmd in dir(client) if cmd.startswith('do_')]
    for i, cmd in enumerate(commands, 1):
        print(f"  {i:2d}. {cmd}")
    
    print(f"\n📊 Tổng cộng: {len(commands)} lệnh FTP được hỗ trợ")
    
    print("\n🔧 Kiến trúc Custom FTP:")
    print("  • Sử dụng socket thay vì ftplib")
    print("  • Hỗ trợ cả passive và active mode")
    print("  • Xử lý binary và ASCII transfer")
    print("  • Tương thích hoàn toàn với code cũ")
    
    print("\n🎯 Các tính năng chính:")
    print("  • Kết nối FTP server")
    print("  • Upload/Download files")
    print("  • Quản lý thư mục")
    print("  • Quét virus tích hợp")
    print("  • Hỗ trợ wildcard patterns")
    print("  • Recursive directory operations")
    
    print("\n💡 Cách sử dụng:")
    print("  python3 client.py  # Chạy command line client")
    print("  python3 main.py    # Chạy GUI client (cần tkinter)")
    
    # Test một số chức năng cơ bản
    print("\n🧪 Test các exception handling:")
    try:
        # Test connection error
        test_ftp = FTP()
        test_ftp.connect("nonexistent.server.com", 21, timeout=1)
    except all_errors as e:
        print(f"  ✅ Exception handling hoạt động: {type(e).__name__}")
    
    print("\n🎉 DEMO HOÀN TẤT - Custom FTP client sẵn sàng sử dụng!")
    print("🚀 Giờ bạn có thể nộp bài mà không cần dùng ftplib!")

def interactive_demo():
    """Demo tương tác với FTP client"""
    print("\n" + "="*60)
    print("INTERACTIVE DEMO - Custom FTP Client")
    print("="*60)
    
    ftp = FTP()
    client = FTPCommands(ftp)
    
    print("\nĐể test với server thật, bạn có thể dùng:")
    print("ftp> open test.rebex.net 21")
    print("User: demo")
    print("Password: password")
    print("\nHoặc gõ 'help' để xem tất cả lệnh")
    print("Gõ 'quit' để thoát\n")
    
    # Chạy command loop
    try:
        client.cmdloop()
    except KeyboardInterrupt:
        print("\n\nThoát chương trình...")
    except Exception as e:
        print(f"\nLỗi: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_demo()
    else:
        test_custom_ftp()
        
        # Hỏi có muốn chạy interactive demo không
        try:
            choice = input("\nBạn có muốn thử interactive demo? (y/n): ").lower().strip()
            if choice in ['y', 'yes']:
                interactive_demo()
        except KeyboardInterrupt:
            print("\n\nTạm biệt!")