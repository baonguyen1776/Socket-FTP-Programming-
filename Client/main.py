import tkinter as tk
from tkinter import messagebox
import sys
import os
import logging

# Thêm thư mục hiện tại vào Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import với error handling
try:
    from login_window import LoginWindow  # type: ignore
    from ftp_gui import FTPClientGUI  # type: ignore
    from utils import Utils  # type: ignore
except ImportError as e:
    print(f"Lỗi import: {e}")
    print("Đảm bảo bạn đang chạy từ thư mục chứa các file Python")
    sys.exit(1)

class FTPClientApp:
    def __init__(self):
        self.root = None
        self.login_window = None
        self.main_gui = None
        self.main_window = None
        self.connection_data = None
        
    def on_disconnect_success(self):
        """Callback khi ngắt kết nối thành công, hiển thị lại cửa sổ đăng nhập"""
        if self.main_window:
            self.main_window.destroy()
            self.main_window = None
            self.main_gui = None
        self.show_login_window()
        
    def start(self):
        """Khởi động ứng dụng"""
        try:
            # Khởi tạo logging
            Utils.log_event("Khởi động FTP Client Application", level=logging.INFO)
            
            # Tạo cửa sổ chính
            self.root = tk.Tk()
            self.root.withdraw()  # Ẩn cửa sổ gốc ngay từ đầu
            
            # Hiển thị cửa sổ đăng nhập
            self.show_login_window()
            
            # Chạy vòng lặp chính
            self.root.mainloop()
            
        except Exception as e:
            print(f"Lỗi khởi động ứng dụng: {e}")
            Utils.log_event(f"Lỗi khởi động ứng dụng: {e}", level=logging.ERROR)
            
    def show_login_window(self):
        """Hiển thị cửa sổ đăng nhập"""
        # Tạo cửa sổ đăng nhập như một Toplevel
        login_root = tk.Toplevel(self.root)
        self.login_window = LoginWindow(login_root, self.on_login_success)
        
    def on_login_success(self, connection_data):
        """Callback khi đăng nhập thành công"""
        self.connection_data = connection_data
        
        # Đóng cửa sổ đăng nhập
        if self.login_window:
            self.login_window.destroy()
        
        # Tạo cửa sổ chính
        self.create_main_window()
        
    def create_main_window(self):
        """Tạo cửa sổ giao diện chính"""
        try:
            # Kiểm tra xem root có còn tồn tại không
            if not self.root or not self.root.winfo_exists():
                # Tạo root mới nếu cần
                self.root = tk.Tk()
                self.root.withdraw()
            
            # Tạo cửa sổ mới cho giao diện chính
            self.main_window = tk.Toplevel(self.root)
            self.main_window.title("FTP Client - Quản lý File")
            self.main_window.geometry("1200x800")
            
            # Khởi tạo giao diện chính với dữ liệu kết nối
            self.main_gui = FTPClientGUI(self.main_window, self.connection_data, self.on_disconnect_success)
            # Xử lý khi đóng cửa sổ chính
            self.main_window.protocol("WM_DELETE_WINDOW", self.on_main_window_close)
            
            # Hiển thị cửa sổ chính
            self.main_window.deiconify()
            self.main_window.lift()
            self.main_window.focus_force()
            
            # Log thành công
            Utils.log_event("Chuyển đổi sang giao diện chính thành công", level=logging.INFO)
            
        except Exception as e:
            Utils.log_event(f"Lỗi tạo cửa sổ chính: {e}", level=logging.ERROR)
            messagebox.showerror("Lỗi", f"Không thể tạo giao diện chính: {e}")
            # Thoát ứng dụng nếu không thể tạo cửa sổ chính
            self.root.quit()
        
    def on_main_window_close(self):
        """Xử lý khi đóng cửa sổ chính"""
        try:
            # Ngắt kết nối FTP nếu còn kết nối
            if self.main_gui and self.main_gui.connected:
                self.main_gui.disconnect_ftp()
                
            # Log
            Utils.log_event("Đóng ứng dụng FTP Client", level=logging.INFO)
            
        except Exception as e:
            Utils.log_event(f"Lỗi khi đóng ứng dụng: {e}", level=logging.ERROR)
            
        finally:
            # Đóng ứng dụng
            if self.root and self.root.winfo_exists():
                self.root.quit()
                self.root.destroy()

def main():
    app = FTPClientApp()
    app.start()

if __name__ == "__main__":
    main()