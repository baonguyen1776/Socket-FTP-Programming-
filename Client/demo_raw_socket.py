#!/usr/bin/env python3
"""
Demo Raw Socket FTP Implementation
Không sử dụng ftplib, chỉ dùng socket thô
"""

import sys
import os
from raw_socket_ftp import *
from ftp_command import FTPCommands

def demo_raw_socket_functions():
    """Demo các function raw socket trực tiếp"""
    print("=== DEMO RAW SOCKET FTP (KHÔNG DÙNG FTPLIB) ===\n")
    
    print("🔧 Các function socket thô có sẵn:")
    functions = [
        "ftp_connect(host, port)",
        "ftp_login(user, pass)", 
        "ftp_send_command(cmd)",
        "ftp_send_line(line)",
        "ftp_recv_line()",
        "ftp_get_response()",
        "ftp_pwd()",
        "ftp_cwd(dirname)",
        "ftp_mkd(dirname)",
        "ftp_rmd(dirname)",
        "ftp_delete(filename)",
        "ftp_rename(old, new)",
        "ftp_size(filename)",
        "ftp_nlst()",
        "ftp_dir()",
        "ftp_retrbinary(cmd, callback)",
        "ftp_retrlines(cmd, callback)",
        "ftp_storbinary(cmd, file)",
        "ftp_storlines(cmd, lines)",
        "ftp_make_pasv()",
        "ftp_make_port()",
        "ftp_transfer_cmd(cmd)",
        "ftp_quit()"
    ]
    
    for i, func in enumerate(functions, 1):
        print(f"  {i:2d}. {func}")
    
    print(f"\n📊 Tổng cộng: {len(functions)} function socket thô")
    
    print("\n🎯 Kiến trúc Raw Socket:")
    print("  • Không có class wrapper phức tạp")
    print("  • Sử dụng global variables để lưu state")
    print("  • Các function độc lập, dễ hiểu")
    print("  • Xử lý trực tiếp socket.socket()")
    print("  • Parse response bằng regex")
    print("  • Hỗ trợ cả passive và active mode")
    
    print("\n💻 Code example:")
    print("""
    # Kết nối trực tiếp bằng raw socket
    ftp_connect('test.rebex.net', 21)
    ftp_login('demo', 'password')
    
    # Lấy thư mục hiện tại
    current_dir = ftp_pwd()
    
    # List files
    files = ftp_nlst()
    
    # Thoát
    ftp_quit()
    """)
    
    print("✅ Raw socket implementation hoàn thành!")
    print("🚀 Không cần ftplib, chỉ cần socket!")

def demo_compatibility_wrapper():
    """Demo wrapper class để tương thích"""
    print("\n" + "="*50)
    print("DEMO COMPATIBILITY WRAPPER")
    print("="*50)
    
    print("\n🔄 Wrapper class FTP() để tương thích với code cũ:")
    print("  • Sử dụng raw socket functions bên trong")
    print("  • Interface giống ftplib.FTP")
    print("  • Không cần thay đổi code hiện tại")
    
    # Test wrapper
    ftp = FTP()
    client = FTPCommands(ftp)
    
    print(f"\n✅ FTP wrapper class khởi tạo thành công!")
    print(f"✅ FTPCommands client sẵn sàng!")
    
    print("\n📋 Các lệnh FTP có sẵn trong client:")
    commands = [cmd[3:] for cmd in dir(client) if cmd.startswith('do_')]
    for i, cmd in enumerate(commands[:10], 1):  # Show first 10
        print(f"  {i:2d}. {cmd}")
    print(f"  ... và {len(commands)-10} lệnh khác")

def interactive_test():
    """Test tương tác với raw socket"""
    print("\n" + "="*50)  
    print("INTERACTIVE TEST - Raw Socket FTP")
    print("="*50)
    
    print("\n🧪 Test kết nối với server demo:")
    print("Host: test.rebex.net")
    print("User: demo") 
    print("Pass: password")
    
    try:
        choice = input("\nBạn có muốn test kết nối thật? (y/n): ").lower().strip()
        if choice in ['y', 'yes']:
            print("\n🔌 Đang kết nối bằng raw socket...")
            
            # Test raw socket functions
            welcome = ftp_connect('test.rebex.net', 21, timeout=10)
            print(f"✅ Kết nối thành công!")
            
            login_resp = ftp_login('demo', 'password')
            print(f"✅ Đăng nhập thành công!")
            
            current_dir = ftp_pwd()
            print(f"📁 Thư mục hiện tại: {current_dir}")
            
            print("📂 Danh sách files:")
            files = ftp_nlst()
            for f in files[:5]:  # Show first 5 files
                print(f"  - {f}")
            if len(files) > 5:
                print(f"  ... và {len(files)-5} file khác")
            
            ftp_quit()
            print("✅ Ngắt kết nối thành công!")
            
        else:
            print("⏭️  Bỏ qua test kết nối thật")
            
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        print("💡 Có thể do network hoặc server không khả dụng")

def show_code_structure():
    """Hiển thị cấu trúc code"""
    print("\n" + "="*50)
    print("CẤU TRÚC CODE RAW SOCKET")
    print("="*50)
    
    print("\n📁 Files đã được cập nhật:")
    files = [
        "raw_socket_ftp.py - Raw socket implementation",
        "ftp_command.py - Updated imports", 
        "ftp_helpers.py - Updated imports",
        "ftp_gui.py - Updated imports",
        "login_window.py - Updated imports",
        "tests/test_real_server.py - Updated imports"
    ]
    
    for f in files:
        print(f"  ✅ {f}")
    
    print("\n🔧 Thay đổi chính:")
    print("  • Thay thế 'from ftplib import' → 'from raw_socket_ftp import'")
    print("  • Tất cả FTP operations giờ dùng socket thô")
    print("  • Tương thích 100% với code cũ")
    print("  • Không cần cài đặt thêm thư viện nào")
    
    print("\n🎯 Lợi ích:")
    print("  • Hiểu rõ giao thức FTP")
    print("  • Kiểm soát hoàn toàn connection")
    print("  • Không phụ thuộc ftplib")
    print("  • Dễ debug và customize")

if __name__ == "__main__":
    demo_raw_socket_functions()
    demo_compatibility_wrapper()
    show_code_structure()
    interactive_test()
    
    print("\n🎉 DEMO HOÀN TẤT!")
    print("🚀 Raw socket FTP client sẵn sàng sử dụng!")
    print("📚 Giờ bạn có thể nộp bài mà không dùng ftplib!")