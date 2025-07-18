import tkinter as tk
from tkinter import ttk, messagebox
import threading
import sys
import os
import socket

# Thêm thư mục hiện tại vào Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ftplib import FTP, all_errors
from config import Config
from utils import Utils
import logging

class LoginWindow:
    def __init__(self, root, on_success_callback):
        self.root = root
        self.on_success_callback = on_success_callback
        self.ftp = None
        self.connected = False
        self.is_connecting = False
        
        # Thiết lập cửa sổ
        self.setup_window()
        self.create_widgets()
        
    def setup_window(self):
        """Thiết lập cửa sổ đăng nhập"""
        self.root.title("FTP Client với Quét Virus")
        self.root.geometry("400x550")  # Tăng chiều cao để có thêm không gian
        self.root.configure(bg='#ecf0f1')  # Màu nền xám nhạt (hiện đại)
        self.root.resizable(False, False)
        
        # Căn giữa cửa sổ
        self.center_window()
        
        # Xử lý sự kiện đóng cửa sổ
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)
        
    def center_window(self):
        """Căn giữa cửa sổ trên màn hình"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_widgets(self):
        """Tạo các widget cho giao diện đăng nhập"""
        # Main container với padding lớn xung quanh
        main_frame = tk.Frame(self.root, bg='#ecf0f1')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        # Title
        title_label = tk.Label(main_frame, text="FTP CLIENT", 
                               font=("Segoe UI", 18, "bold"), fg='#2c3e50', bg='#ecf0f1')
        title_label.pack(pady=(0, 40))
        
        # Form fields
        self.create_form_fields(main_frame)
        
        # Login button
        self.create_login_button(main_frame)
        
        # Status message
        self.status_var = tk.StringVar(value="Sẵn sàng kết nối...")
        self.status_label = tk.Label(main_frame, textvariable=self.status_var, 
                                     font=("Segoe UI", 10), fg="#111f3f", bg='#ecf0f1')
        self.status_label.pack(pady=(20, 0))
        
    def create_form_fields(self, parent):
        """Tạo các field nhập liệu"""
        # Host
        tk.Label(parent, text="Địa chỉ FTP Server:", 
                 font=("Segoe UI", 12), fg='#2c3e50', bg='#ecf0f1').pack(anchor=tk.W, pady=(0, 8))
        self.host_var = tk.StringVar(value="")
        host_entry = tk.Entry(parent, textvariable=self.host_var, 
                             font=("Segoe UI", 12), bg="white", bd=0, relief=tk.FLAT, highlightthickness=1, highlightbackground="#bdc3c7", highlightcolor="#3498db")
        host_entry.pack(fill=tk.X, pady=(0, 20), ipady=10)
        
        # Port
        tk.Label(parent, text="Cổng:", 
                 font=("Segoe UI", 12), fg='#2c3e50', bg='#ecf0f1').pack(anchor=tk.W, pady=(0, 8))
        self.port_var = tk.StringVar(value="")
        port_entry = tk.Entry(parent, textvariable=self.port_var, 
                             font=("Segoe UI", 12), bg="white", bd=0, relief=tk.FLAT, highlightthickness=1, highlightbackground="#bdc3c7", highlightcolor="#3498db")
        port_entry.pack(fill=tk.X, pady=(0, 20), ipady=10)
        
        # Username
        tk.Label(parent, text="Tên đăng nhập:", 
                 font=("Segoe UI", 12), fg='#2c3e50', bg='#ecf0f1').pack(anchor=tk.W, pady=(0, 8))
        self.username_var = tk.StringVar(value="")
        username_entry = tk.Entry(parent, textvariable=self.username_var, 
                                  font=("Segoe UI", 12), bg="white", bd=0, relief=tk.FLAT, highlightthickness=1, highlightbackground="#bdc3c7", highlightcolor="#3498db")
        username_entry.pack(fill=tk.X, pady=(0, 20), ipady=10)
        
        # Password
        tk.Label(parent, text="Mật khẩu:", 
                 font=("Segoe UI", 12), fg='#2c3e50', bg='#ecf0f1').pack(anchor=tk.W, pady=(0, 8))
        self.password_var = tk.StringVar(value="")
        password_entry = tk.Entry(parent, textvariable=self.password_var, 
                                  font=("Segoe UI", 12), bg="white", bd=0, relief=tk.FLAT, highlightthickness=1, highlightbackground="#bdc3c7", highlightcolor="#3498db", show="*")
        password_entry.pack(fill=tk.X, pady=(0, 20), ipady=10)
        password_entry.bind("<Return>", lambda e: self.connect_ftp())
        
    def create_login_button(self, parent):
        """Tạo nút đăng nhập"""
        # NÚT ĐĂNG NHẬP CHÍNH
        self.login_btn = tk.Button(parent, 
                                 text="KẾT NỐI", 
                                 font=("Segoe UI", 14, "bold"), 
                                 fg='white', 
                                 bg='#27ae60',
                                 activebackground='#2ecc71',
                                 relief=tk.FLAT, 
                                 bd=0, 
                                 highlightthickness=0,
                                 pady=12,
                                 cursor='hand2',
                                 command=self.connect_ftp)
        self.login_btn.pack(fill=tk.X, pady=(10, 0))
        
        # Hiệu ứng hover cho nút (đổi màu khi di chuột)
        def on_enter(event):
            if not self.is_connecting:
                self.login_btn.configure(bg='#2ecc71')
        def on_leave(event):
            if not self.is_connecting:
                self.login_btn.configure(bg='#27ae60')
        self.login_btn.bind("<Enter>", on_enter)
        self.login_btn.bind("<Leave>", on_leave)
        
    def connect_ftp(self):
        """Kết nối FTP"""
        if self.is_connecting:
            return
            
        # Lấy thông tin từ các trường nhập
        host = self.host_var.get().strip()
        port = self.port_var.get().strip()
        username = self.username_var.get().strip()
        password = self.password_var.get()
        
        # Kiểm tra đầu vào
        if not host:
            self.show_status("Vui lòng nhập địa chỉ FTP Server", "error")
            return
        if not username:
            self.show_status("Vui lòng nhập tên đăng nhập", "error")
            return
        try:
            port = int(port)
        except ValueError:
            self.show_status("Cổng phải là số", "error")
            return
            
        # Vô hiệu hóa nút và cập nhật trạng thái
        self.is_connecting = True
        self.login_btn.configure(text="ĐANG KẾT NỐI...", state=tk.DISABLED, bg='#95a5a6')
        
        def connect_thread():
            try:
                self.safe_after(lambda: self.show_status("Đang kiểm tra kết nối mạng...", "info"))
                
                # Thử kết nối mạng trước
                try:
                    socket.create_connection((host, port), timeout=10)
                except socket.error as e:
                    raise Exception(f"Không thể kết nối đến {host}:{port}. Chi tiết: {str(e)}")
                
                self.safe_after(lambda: self.show_status("Đang kết nối FTP...", "info"))
                
                # Kết nối FTP
                self.ftp = FTP()
                self.ftp.connect(host, port, timeout=30)
                
                self.safe_after(lambda: self.show_status("Đang đăng nhập...", "info"))
                
                # Đăng nhập
                if username.lower() == "anonymous":
                    self.ftp.login()
                else:
                    self.ftp.login(username, password)
                
                # Bật chế độ passive (mặc định True)
                self.ftp.set_pasv(True)
                
                self.connected = True
                self.safe_after(self.on_connect_success)
                
            except Exception as e:
                error_msg = f"Lỗi kết nối: {str(e)}"
                self.safe_after(lambda: self.on_connect_error(error_msg))
                
        # Kết nối sử dụng thread để không chặn GUI
        threading.Thread(target=connect_thread, daemon=True).start()
        
    def safe_after(self, callback):
        """Safely schedule callback in main thread"""
        try:
            if self.root and self.root.winfo_exists():
                self.root.after(0, callback)
        except tk.TclError:
            # Cửa sổ có thể đã bị đóng
            pass
            
    def on_connect_success(self):
        """Kết nối thành công"""
        if not self.root or not self.root.winfo_exists():
            return
        self.show_status("Kết nối thành công! Đang chuyển...", "success")
        
        connection_data = {
            'ftp': self.ftp,
            'host': self.host_var.get(),
            'port': int(self.port_var.get()),
            'username': self.username_var.get(),
            'passive_mode': True,  # Mặc định True
            'auto_scan': True      # Mặc định True
        }
        # Chuyển đối tượng FTP sang cửa sổ chính và đặt lại trạng thái
        self.ftp = None
        self.connected = False
        # Gọi callback (mở cửa sổ chính) sau một chút thời gian
        self.root.after(100, lambda: self.on_success_callback(connection_data))
        
    def on_connect_error(self, error_msg):
        """Kết nối lỗi"""
        if not self.root or not self.root.winfo_exists():
            return
        # Thông báo lỗi kèm gợi ý khắc phục
        if "connection refused" in error_msg.lower():
            error_msg += "\n Gợi ý: FTP server chưa khởi động hoặc cổng bị chặn"
        elif "timed out" in error_msg.lower():
            error_msg += "\n Gợi ý: Kiểm tra địa chỉ IP và đảm bảo FTP server đang chạy"
        elif "login" in error_msg.lower():
            error_msg += "\n Gợi ý: Kiểm tra tên đăng nhập và mật khẩu"
        self.show_status(error_msg, "error")
        self.is_connecting = False
        # Kích hoạt lại nút kết nối
        self.login_btn.configure(text="KẾT NỐI", state=tk.NORMAL, bg='#27ae60')
        
    def show_status(self, message, status_type="info"):
        """Hiển thị trạng thái"""
        if not self.root or not self.root.winfo_exists():
            return
        colors = {
            "info": "#3498db",
            "success": "#27ae60", 
            "error": "#e74c3c",
            "warning": "#f39c12"
        }
        self.status_var.set(message)
        self.status_label.configure(fg=colors.get(status_type, "#3498db"))
        
    def on_window_close(self):
        """Xử lý khi đóng cửa sổ"""
        if self.ftp and self.connected:
            try:
                self.ftp.quit()
            except:
                pass
        
        Utils.log_event("Đã đóng ứng dụng FTP Client", level=logging.INFO)
        self.root.destroy()
        sys.exit(0)
        
    def destroy(self):
        """Đóng cửa sổ"""
        # Đóng kết nối FTP nếu còn mở (trừ khi đã chuyển sang cửa sổ chính)
        if self.ftp and self.connected:
            try:
                self.ftp.quit()
            except:
                pass
        if hasattr(self, 'root') and self.root:
            try:
                self.root.destroy()
            except tk.TclError:
                pass
