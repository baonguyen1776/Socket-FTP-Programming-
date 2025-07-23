import tkinter as tk
from tkinter import ttk, messagebox
import threading
import sys
import os
import socket

# Thêm thư mục hiện tại vào Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from custom_ftp import FTP, all_errors
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
        self.root.geometry("400x700")
        # Nền gradient như trong hình (tím nhạt)
        self.root.configure(bg="#ecf0f1")
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
        # Main container
        main_frame = tk.Frame(self.root, bg='#b8a9d9')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=60)
        
        # Glassmorphism card - màu trắng trong suốt
        card_frame = tk.Frame(main_frame, bg='#ffffff', relief=tk.FLAT, bd=0)
        # Tạo hiệu ứng bo góc bằng cách đặt highlightthickness
        card_frame.configure(highlightbackground='#ffffff', highlightcolor='#ffffff', highlightthickness=1)
        card_frame.pack(fill=tk.BOTH, expand=True)
        
        # Icon global
        icon_frame = tk.Frame(card_frame, bg='#ffffff', height=100)
        icon_frame.pack(fill=tk.X, pady=(30, 20))
        icon_frame.pack_propagate(False)
        
        # Icon với border tròn
        icon_bg = tk.Frame(icon_frame, bg='#ffffff', width=70, height=70)
        icon_bg.pack(anchor=tk.CENTER)
        icon_bg.pack_propagate(False)
        
        # Icon global
        global_icon = tk.Label(icon_bg, text="🌐", font=("Arial", 20), 
                              bg='#ffffff', fg='#666666')
        global_icon.pack(expand=True)

        # Vẽ border tròn cho icon (giả lập)
        canvas = tk.Canvas(icon_frame, width=80, height=80, bg='#ffffff', highlightthickness=0)
        canvas.pack(anchor=tk.CENTER)
        canvas.create_oval(10, 10, 70, 70, outline='#cccccc', width=2)
        canvas.create_text(40, 40, text="🌐", font=("Arial", 20), fill='#666666')
        
        # Form fields container
        form_frame = tk.Frame(card_frame, bg='#ffffff')
        form_frame.pack(fill=tk.X, padx=40, pady=20)
        
        # Create form fields
        self.create_form_fields(form_frame)
        
        # Login button
        self.create_login_button(form_frame)
        
        # Status message
        self.status_var = tk.StringVar(value="Kết nối đến FTP Server")
        self.status_label = tk.Label(card_frame, textvariable=self.status_var, 
                                     font=("Arial", 9), fg="#666666", bg='#ffffff')
        self.status_label.pack(pady=(10, 20))
        
    def create_form_fields(self, parent):
        """Tạo các field nhập liệu"""
        # Host field
        host_frame = tk.Frame(parent, bg='#f5f5f5', relief=tk.FLAT, bd=0, height=45)
        host_frame.pack(fill=tk.X, pady=(0, 12))
        host_frame.pack_propagate(False)
        
        # Icon
        tk.Label(host_frame, text="👤", font=("Arial", 14), bg='#f5f5f5', fg='#999999').pack(side=tk.LEFT, padx=(12, 8), pady=12)
        
        # Entry field
        self.host_var = tk.StringVar(value="")
        host_entry = tk.Entry(host_frame, textvariable=self.host_var, 
                             font=("Arial", 11), bg='#f5f5f5', fg='#333333', bd=0, 
                             relief=tk.FLAT, insertbackground='#666666')
        host_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=12, padx=(0, 12))
        host_entry.config(highlightthickness=0)
        
        # Placeholder
        self.add_placeholder(host_entry, "Địa chỉ FTP Server")
        
        # Port field
        port_frame = tk.Frame(parent, bg='#f5f5f5', relief=tk.FLAT, bd=0, height=45)
        port_frame.pack(fill=tk.X, pady=(0, 12))
        port_frame.pack_propagate(False)
        
        tk.Label(port_frame, text="🔌", font=("Arial", 14), bg='#f5f5f5', fg='#999999').pack(side=tk.LEFT, padx=(12, 8), pady=12)
        
        self.port_var = tk.StringVar(value="")
        port_entry = tk.Entry(port_frame, textvariable=self.port_var, 
                             font=("Arial", 11), bg='#f5f5f5', fg='#333333', bd=0, 
                             relief=tk.FLAT, insertbackground='#666666')
        port_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=12, padx=(0, 12))
        port_entry.config(highlightthickness=0)
        
        # Placeholder
        self.add_placeholder(port_entry, "Cổng")
        
        # Username field  
        username_frame = tk.Frame(parent, bg='#f5f5f5', relief=tk.FLAT, bd=0, height=45)
        username_frame.pack(fill=tk.X, pady=(0, 12))
        username_frame.pack_propagate(False)
        
        tk.Label(username_frame, text="👤", font=("Arial", 14), bg='#f5f5f5', fg='#999999').pack(side=tk.LEFT, padx=(12, 8), pady=12)
        
        self.username_var = tk.StringVar(value="")
        username_entry = tk.Entry(username_frame, textvariable=self.username_var, 
                                  font=("Arial", 11), bg='#f5f5f5', fg='#333333', bd=0, 
                                  relief=tk.FLAT, insertbackground='#666666')
        username_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=12, padx=(0, 12))
        username_entry.config(highlightthickness=0)
        
        # Placeholder
        self.add_placeholder(username_entry, "Tên đăng nhập")
        
        # Password field
        password_frame = tk.Frame(parent, bg='#f5f5f5', relief=tk.FLAT, bd=0, height=45)
        password_frame.pack(fill=tk.X, pady=(0, 12))
        password_frame.pack_propagate(False)
        
        tk.Label(password_frame, text="🔒", font=("Arial", 14), bg='#f5f5f5', fg='#999999').pack(side=tk.LEFT, padx=(12, 8), pady=12)
        
        self.password_var = tk.StringVar(value="")
        password_entry = tk.Entry(password_frame, textvariable=self.password_var, 
                                  font=("Arial", 11), bg='#f5f5f5', fg='#333333', bd=0, 
                                  relief=tk.FLAT, insertbackground='#666666', show="*")
        password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=12, padx=(0, 12))
        password_entry.config(highlightthickness=0)
        password_entry.bind("<Return>", lambda e: self.connect_ftp())
        
        # Placeholder
        self.add_placeholder(password_entry, "Mật khẩu")
        
    def add_placeholder(self, entry, placeholder_text):
        """Thêm placeholder text cho entry"""
        entry.insert(0, placeholder_text)
        entry.config(fg='#999999')
        
        def on_focus_in(event):
            if entry.get() == placeholder_text:
                entry.delete(0, tk.END)
                entry.config(fg='#333333')
        
        def on_focus_out(event):
            if entry.get() == "":
                entry.insert(0, placeholder_text)
                entry.config(fg='#999999')
        
        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)
        
    def create_login_button(self, parent):
        """Tạo nút đăng nhập"""
        self.login_btn = tk.Button(parent, 
                                 text="LOGIN", 
                                 font=("Arial", 12, "bold"), 
                                 fg='#ffffff', 
                                 bg="#1976d2",
                                 activebackground='#1565c0',
                                 activeforeground='#ffffff',
                                 relief=tk.FLAT, 
                                 bd=1, 
                                 highlightthickness=1,
                                 highlightbackground='#1565c0',
                                 highlightcolor='#1565c0',
                                 pady=12,
                                 cursor='hand2',
                                 command=self.connect_ftp)
        self.login_btn.pack(fill=tk.X, pady=(0, 12))
        
        # Hiệu ứng hover
        def on_enter(event):
            if not self.is_connecting:
                self.login_btn.configure(bg='#1565c0')
        def on_leave(event):
            if not self.is_connecting:
                self.login_btn.configure(bg='#1976d2')
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
        
        # Bỏ qua placeholder text
        if host == "Địa chỉ FTP Server":
            host = ""
        if port == "Cổng":
            port = ""
        if username == "Tên đăng nhập":
            username = ""
        if password == "Mật khẩu":
            password = ""
        
        # Kiểm tra đầu vào
        if not host:
            self.show_status("Vui lòng nhập địa chỉ FTP Server", "error")
            return
        if not username:
            self.show_status("Vui lòng nhập tên đăng nhập", "error")
            return
        try:
            port = int(port) if port else 21
        except ValueError:
            self.show_status("Cổng phải là số", "error")
            return
            
        # Vô hiệu hóa nút và cập nhật trạng thái
        self.is_connecting = True
        self.login_btn.configure(text="ĐANG KẾT NỐI...", state=tk.DISABLED, bg='#f0f0f0')
        
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
            'port': int(self.port_var.get()) if self.port_var.get() and self.port_var.get() != "Cổng" else 21,
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
        self.login_btn.configure(text="LOGIN", state=tk.NORMAL, bg='#ffffff')
        
    def show_status(self, message, status_type="info"):
        """Hiển thị trạng thái"""
        if not self.root or not self.root.winfo_exists():
            return
        colors = {
            "info": "#666666",
            "success": "#4caf50", 
            "error": "#f44336",
            "warning": "#ff9800"
        }
        self.status_var.set(message)
        self.status_label.configure(fg=colors.get(status_type, "#666666"))
        
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