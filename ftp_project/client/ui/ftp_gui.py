import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import time
import threading
import os
import concurrent.futures
import sys
import sys
import glob
import fnmatch

# Thêm thư mục hiện tại vào Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ..core.raw_socket_ftp import FTP, all_errors, error_perm, error_temp, error_proto
from ..core.ftp_command import FTPCommands
from ..core.virus_scan import VirusScan
from ..core.ftp_helpers import FTPHelpers
from ..core.utils import Utils
from ..core.config import Config
import logging
from datetime import datetime

class ProgressWindow:
    """Cửa sổ hiển thị tiến trình với thanh progress bar"""
    
    def __init__(self, parent, title="Đang xử lý..."):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("450x200")
        self.window.resizable(False, False)
        self.window.configure(bg='#ffffff')
        self.window.transient(parent)
        self.window.grab_set()
        
        # Center window
        self.center_window()
        
        # Variables
        self.is_cancelled = False
        self.progress_var = tk.DoubleVar()
        
        # Create UI
        self.create_ui()
        
    def center_window(self):
        """Căn giữa cửa sổ"""
        self.window.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - 225
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - 100
        self.window.geometry(f"450x200+{x}+{y}")
        
    def create_ui(self):
        """Tạo giao diện"""
        main_frame = tk.Frame(self.window, bg='#ffffff')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Icon
        icon_label = tk.Label(main_frame, text="⚡", font=('Segoe UI', 24),
                             bg='#ffffff', fg='#3b82f6')
        icon_label.pack(pady=(0, 15))
        
        # Status label
        self.status_label = tk.Label(main_frame, text="Đang chuẩn bị...",
                                   font=('Segoe UI', 10),
                                   bg='#ffffff',
                                   fg='#374151')
        self.status_label.pack(pady=(0, 15))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(main_frame,
                                          variable=self.progress_var,
                                          maximum=100,
                                          length=350)
        self.progress_bar.pack(pady=(0, 10))
        
        # Percentage label
        self.percent_label = tk.Label(main_frame, text="0%",
                                    font=('Segoe UI', 10, 'bold'),
                                    bg='#ffffff',
                                    fg='#3b82f6')
        self.percent_label.pack(pady=(0, 15))
        
        # Cancel button
        self.cancel_btn = tk.Button(main_frame, text="Hủy bỏ",
                                   bg='#ef4444', fg='white',
                                   command=self.cancel)
        self.cancel_btn.pack()
        
    def update_progress(self, percent, status_text=""):
        """Cập nhật tiến trình"""
        self.progress_var.set(percent)
        self.percent_label.configure(text=f"{percent:.1f}%")
        if status_text:
            self.status_label.configure(text=status_text)
        self.window.update_idletasks()
        
    def cancel(self):
        """Hủy bỏ tiến trình"""
        self.is_cancelled = True
        self.close()
        
    def close(self):
        """Đóng cửa sổ"""
        self.window.destroy()


class FTPClientGUI:
    def __init__(self, root, connection_data=None, on_disconnect=None):
        self.root = root
        self.on_disconnect = on_disconnect
        self.root.title("FTP Client với Quét Virus - Quản lý File")
        self.root.geometry("1300x800")
        self.root.configure(bg='#f0f0f0')

        # Khởi tạo các biến
        if connection_data:
            self.ftp = connection_data['ftp']
            self.ftp_cmd = FTPCommands(self.ftp)
            self.connected = True
            self.current_remote_dir = self.ftp.pwd() if self.ftp else "/"
            self.passive_mode = connection_data.get('passive_mode', True)
            self.auto_scan_enabled = connection_data.get('auto_scan', True)
            self.connection_info = {
                'host': connection_data.get('host', ''),
                'port': connection_data.get('port', 21),
                'username': connection_data.get('username', '')
            }
        else:
            self.ftp = None
            self.connected = False
            self.current_remote_dir = "/"
            self.passive_mode = True
            self.auto_scan_enabled = True
            self.connection_info = {}

        self.ftp_helpers = FTPHelpers(self.ftp, self.root) if self.ftp else None

        self.virus_scanner = VirusScan()
        self.current_local_dir = os.getcwd()
        self.transfer_mode = 'binary'
        self.prompt_on_mget_mput = True

        # Tạo giao diện
        self.transfer_mode_var = tk.StringVar(value="binary")
        self.passive_mode_var = tk.BooleanVar(value=self.passive_mode)
        self.create_widgets()
        self.update_local_files()

        # Log và cập nhật giao diện nếu đã kết nối
        if self.connected:
            self.log_message(f"Đã kết nối tới {self.connection_info.get('host', 'FTP Server')}", "INFO")
            self.update_connection_status()
            self.update_remote_files()
            self.root.protocol("WM_DELETE_WINDOW", self.do_quit)
        else:
            self.log_message("FTP Client đã khởi động", "INFO")

    def set_transfer_mode(self):
        mode = self.transfer_mode_var.get()
        if mode == "ascii":
            self.ftp_cmd.voidcmd("TYPE A")
        else:
            self.ftp_cmd.voidcmd("TYPE I")
        self.transfer_mode = mode
        self.log_message(f"Đã chuyển sang chế độ truyền: {mode.upper()}")

    def toggle_passive_mode(self):
        self.passive_mode = self.passive_mode_var.get()
        if self.connected:
            self.ftp_cmd.set_pasv(self.passive_mode)
        self.log_message(f"Passive FTP mode: {'ON' if self.passive_mode else 'OFF'}")

    def create_widgets(self):
        """Tạo các widget cho giao diện"""
        # Main frame
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top button frame
        top_button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        top_button_frame.pack(fill=tk.X, pady=(0, 5))

        # Disconnect button
        self.disconnect_btn = tk.Button(top_button_frame, text="🔚 Disconnect", command=self.disconnect_ftp, 
                                        bg='#F44336', fg='white', state=tk.DISABLED)
        self.disconnect_btn.pack(side=tk.LEFT, padx=2)

        # Transfer mode label
        tk.Label(top_button_frame, text="Transfer Mode:", bg='#f0f0f0').pack(side=tk.LEFT, padx=(10, 2))

        # Binary / ASCII Radiobuttons
        tk.Radiobutton(top_button_frame, text="Binary", 
                       variable=self.transfer_mode_var, value="binary",
                       bg='#f0f0f0', command=self.set_transfer_mode, state=tk.NORMAL).pack(side=tk.LEFT)
        tk.Radiobutton(top_button_frame, text="ASCII", 
                       variable=self.transfer_mode_var, value="ascii",
                       bg='#f0f0f0', command=self.set_transfer_mode, state=tk.NORMAL).pack(side=tk.LEFT)

        # Passive mode toggle
        tk.Checkbutton(top_button_frame, text="Passive Mode", 
                       variable=self.passive_mode_var,
                       bg='#f0f0f0', command=self.toggle_passive_mode, state=tk.NORMAL).pack(side=tk.LEFT, padx=10)

        # Prompt toggle
        self.prompt_btn = tk.Button(top_button_frame, text="🔁 Prompt", command=self.do_prompt, 
                                    bg='#795548', fg='white')
        self.prompt_btn.pack(side=tk.LEFT, padx=2)

        self.quit_btn = tk.Button(top_button_frame, text="❌ Exit", command=self.do_quit, 
                          bg='#e74c3c', fg='white')
        self.quit_btn.pack(side=tk.RIGHT, padx=2)

        # Status
        self.status_btn = tk.Button(top_button_frame, text="ℹ️ Status", command=self.do_status, 
                                    bg='#607D8B', fg='white')
        self.status_btn.pack(side=tk.LEFT, padx=2)

        # Status bar
        self.status_var = tk.StringVar(value="Chưa kết nối")
        self.status_label = tk.Label(main_frame, textvariable=self.status_var, 
                                   font=("Arial", 10), bd=1, relief=tk.SUNKEN, anchor=tk.W,
                                   bg='#f0f0f0', fg='red')
        self.status_label.pack(fill=tk.X, pady=(0, 10))

        # PanedWindow để chia màn hình
        paned_window = tk.PanedWindow(main_frame, orient=tk.HORIZONTAL, bg='#f0f0f0')
        paned_window.pack(fill=tk.BOTH, expand=True)

        # Local files frame
        local_frame = tk.Frame(paned_window, bg='#f0f0f0')
        paned_window.add(local_frame)

        # Remote files frame
        remote_frame = tk.Frame(paned_window, bg='#f0f0f0')
        paned_window.add(remote_frame)

        # Local files
        tk.Label(local_frame, text="Local Files", font=("Arial", 12, "bold"), bg='#f0f0f0').pack(fill=tk.X)
        
        # Local path and buttons
        local_path_frame = tk.Frame(local_frame, bg='#f0f0f0')
        local_path_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.local_path_var = tk.StringVar(value=self.current_local_dir)
        tk.Label(local_path_frame, textvariable=self.local_path_var, bg='#f0f0f0', 
                 anchor=tk.W, relief=tk.SUNKEN, bd=1, padx=5).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Button(local_path_frame, text="📁 Browse", command=self.select_local_directory, 
                  bg='#4CAF50', fg='white').pack(side=tk.RIGHT)

        # Local treeview
        self.local_tree = ttk.Treeview(local_frame, columns=("Size", "Modified"), selectmode=tk.BROWSE)
        self.local_tree.heading("#0", text="Name")
        self.local_tree.heading("Size", text="Size")
        self.local_tree.heading("Modified", text="Modified")
        self.local_tree.column("#0", width=300)
        self.local_tree.column("Size", width=120)
        self.local_tree.column("Modified", width=180)
        
        scroll_local = ttk.Scrollbar(local_frame, orient=tk.VERTICAL, command=self.local_tree.yview)
        self.local_tree.configure(yscrollcommand=scroll_local.set)
        
        self.local_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.local_tree.bind("<Double-1>", self.on_local_double_click)
        scroll_local.pack(side=tk.RIGHT, fill=tk.Y)

        # Local buttons
        local_btn_frame = tk.Frame(local_frame, bg='#f0f0f0')
        local_btn_frame.pack(side=tk.TOP, fill=tk.X, pady=(5, 0))
        
        tk.Button(local_btn_frame, text="🔄 Refresh", command=self.update_local_files, 
                  bg='#2196F3', fg='white').pack(side=tk.LEFT, padx=2)
        self.upload_btn = tk.Button(local_btn_frame, text="⬆️ Upload", command=self.do_put, 
                                   bg='#4CAF50', fg='white', state=tk.DISABLED)
        self.upload_btn.pack(side=tk.LEFT, padx=2)
        self.mput_btn = tk.Button(local_btn_frame, text="📤 Mput", command=self.do_mput, 
                                 bg='#4CAF50', fg='white', state=tk.DISABLED)
        self.mput_btn.pack(side=tk.LEFT, padx=2)
        self.putdir_btn = tk.Button(local_btn_frame, text="📂 Upload Folder", command=self.do_putdir,
                                 bg='#4CAF50', fg='white', state=tk.DISABLED)
        self.putdir_btn.pack(side=tk.LEFT, padx=2)

        # Remote files
        tk.Label(remote_frame, text="Remote Server", font=("Arial", 12, "bold"), bg='#f0f0f0').pack(fill=tk.X)
        
        # Remote path
        self.remote_path_var = tk.StringVar(value=self.current_remote_dir)
        self.remote_path_entry = tk.Entry(remote_frame, textvariable=self.remote_path_var, relief=tk.SUNKEN)
        self.remote_path_entry.pack(fill=tk.X, pady=(0, 5))
        self.remote_path_entry.bind("<Return>", self.on_remote_path_enter)

        # Remote treeview
        self.remote_tree = ttk.Treeview(remote_frame, columns=("Size", "Modified"), selectmode=tk.BROWSE)
        self.remote_tree.heading("#0", text="Name")
        self.remote_tree.heading("Size", text="Size")
        self.remote_tree.heading("Modified", text="Modified")
        self.remote_tree.column("#0", width=300)
        self.remote_tree.column("Size", width=120)
        self.remote_tree.column("Modified", width=180)
        
        scroll_remote = ttk.Scrollbar(remote_frame, orient=tk.VERTICAL, command=self.remote_tree.yview)
        self.remote_tree.configure(yscrollcommand=scroll_remote.set)
        
        self.remote_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.remote_tree.bind("<Double-1>", self.on_remote_double_click)
        scroll_remote.pack(side=tk.RIGHT, fill=tk.Y)

        # Remote buttons
        remote_btn_frame = tk.Frame(remote_frame, bg='#f0f0f0')
        remote_btn_frame.pack(side=tk.TOP, fill=tk.X, pady=(5, 0))
        
        self.refresh_remote_btn = tk.Button(remote_btn_frame, text="🔄 Refresh", command=self.update_remote_files, 
                                bg='#2196F3', fg='white', state=tk.DISABLED)
        self.refresh_remote_btn.pack(side=tk.LEFT, padx=2)
        self.download_btn = tk.Button(remote_btn_frame, text="⬇️ Download", command=self.do_get, 
                                bg='#FF9800', fg='white', state=tk.DISABLED)
        self.download_btn.pack(side=tk.LEFT, padx=2)
        self.mget_btn = tk.Button(remote_btn_frame, text="📥 Mget", command=self.do_mget, 
                                bg='#FF9800', fg='white', state=tk.DISABLED)
        self.mget_btn.pack(side=tk.LEFT, padx=2)
        self.create_folder_btn = tk.Button(remote_btn_frame, text="🆕 New Folder", command=self.create_remote_folder, 
                                bg='#607D8B', fg='white', state=tk.DISABLED)
        self.create_folder_btn.pack(side=tk.LEFT, padx=2)
        self.delete_remote_btn = tk.Button(remote_btn_frame, text="🗑️ Delete", command=self.delete_remote_item, 
                                bg='#F44336', fg='white', state=tk.DISABLED)
        self.delete_remote_btn.pack(side=tk.LEFT, padx=2)
        self.rename_remote_btn = tk.Button(remote_btn_frame, text="✏️ Rename", command=self.rename_remote_item, 
                                bg='#9C27B0', fg='white', state=tk.DISABLED)
        self.rename_remote_btn.pack(side=tk.LEFT, padx=2)
        self.getdir_btn = tk.Button(remote_btn_frame, text="📂 Download Folder", command=self.do_getdir,
                                bg='#FF9800', fg='white', state=tk.DISABLED)
        self.getdir_btn.pack(side=tk.LEFT, padx=2)
        
        # Log area
        log_frame = tk.Frame(main_frame, bg='#f0f0f0')
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        tk.Label(log_frame, text="Log", font=("Arial", 12, "bold"), bg='#f0f0f0').pack(anchor=tk.W)
        
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, height=8, state=tk.NORMAL)
        scroll_log = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scroll_log.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.progress = ttk.Progressbar(log_frame, orient="horizontal", mode="determinate")
        self.progress.pack(fill=tk.X, pady=(5, 0))

        scroll_log.pack(side=tk.RIGHT, fill=tk.Y)
        
        clear_log_btn = tk.Button(log_frame, text="🧹 Clear Log", command=self.clear_log, 
                                 bg='#607D8B', fg='white')
        clear_log_btn.pack(side=tk.BOTTOM, anchor=tk.E, pady=(5, 0))

    def _ftp_cmd(self, func, *args, **kwargs):
        """Wrapper để thực hiện lệnh FTP và xử lý lỗi chung"""
        if not self.connected:
            messagebox.showerror("Error", "Not connected to FTP server")
            return None
        try:
            # Đảm bảo chế độ passive được đặt đúng trước khi truyền dữ liệu
            is_data_transfer = func.__name__ in (
                'nlst', 'retrbinary', 'retrlines', 'storbinary', 'storlines', 'dir'
            )
            if is_data_transfer:
                self.ftp.set_pasv(self.passive_mode)

            return func(*args, **kwargs)
        except error_perm as e:
            self.log_message(f"FTP permission error: {e}", "ERROR")
            messagebox.showerror("Error", f"FTP permission error: {e}")
        except error_temp as e:
            self.log_message(f"FTP temporary error: {e}", "ERROR")
            messagebox.showerror("Error", f"FTP temporary error: {e}")
        except error_proto as e:
            self.log_message(f"FTP protocol error: {e}", "ERROR")
            messagebox.showerror("Error", f"FTP protocol error: {e}")
        except all_errors as e:
            self.log_message(f"FTP error: {e}", "ERROR")
            messagebox.showerror("Error", f"FTP error: {e}")
        except Exception as e:
            self.log_message(f"Error: {e}", "ERROR")
            messagebox.showerror("Error", f"Error: {e}")
        return None

    def disconnect_ftp(self):
        """Ngắt kết nối FTP và gọi lại màn hình đăng nhập"""
        if self.ftp:
            try:
                self._ftp_cmd(self.ftp.quit)
                self.log_message("Đã ngắt kết nối FTP.", "INFO")
            except Exception as e:
                self.log_message(f"Lỗi khi ngắt kết nối FTP: {e}", "ERROR")
            finally:
                self.ftp = None
                self.connected = False
                self.ftp_helpers = None
                self.update_connection_status()
                self.remote_tree.delete(*self.remote_tree.get_children())

        if self.on_disconnect:
            self.on_disconnect()

    def select_local_directory(self):
        """Chọn thư mục local"""
        directory = filedialog.askdirectory(initialdir=self.current_local_dir)
        if directory:
            self.current_local_dir = directory
            self.local_path_var.set(directory)
            self.update_local_files()
            self.log_message(f"Đã chuyển đến thư mục: {directory}")

    def update_local_files(self):
        """Cập nhật danh sách file local"""
        self.local_tree.delete(*self.local_tree.get_children())

        if os.path.dirname(self.current_local_dir) != self.current_local_dir:
            self.local_tree.insert("", tk.END, text="📁 /..", values=("", ""))

        try:
            for item in os.listdir(self.current_local_dir):
                item_path = os.path.join(self.current_local_dir, item)

                if os.path.isdir(item_path):
                    self.local_tree.insert("", tk.END, text=f"📁 {item}", values=("", ""))
                else:
                    size = os.path.getsize(item_path)
                    modified = datetime.fromtimestamp(os.path.getmtime(item_path)).strftime("%Y-%m-%d %H:%M")
                    self.local_tree.insert("", tk.END, text=f"📄 {item}", values=(f"{size:,} bytes", modified))

        except Exception as e:
            self.log_message(f"Lỗi đọc thư mục local: {str(e)}", "ERROR")

    def log_message(self, message, level="INFO"):
        """Thêm message vào log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}\n"

        if hasattr(self, "log_text"):
            self.log_text.insert(tk.END, log_entry)
            self.log_text.see(tk.END)

        # Log vào file
        Utils.log_event(message, level=getattr(logging, level, logging.INFO))

    def update_connection_status(self):
        """Cập nhật trạng thái kết nối trong giao diện"""
        if self.connected:
            host = self.connection_info.get('host', 'Unknown')
            self.status_var.set(f"Đã kết nối - {host}")
            self.status_label.configure(foreground="green")

            # Enable các nút
            self.disconnect_btn.configure(state=tk.NORMAL)
            self.refresh_remote_btn.configure(state=tk.NORMAL)
            self.create_folder_btn.configure(state=tk.NORMAL)
            self.delete_remote_btn.configure(state=tk.NORMAL)
            self.rename_remote_btn.configure(state=tk.NORMAL)
            self.upload_btn.configure(state=tk.NORMAL)
            self.download_btn.configure(state=tk.NORMAL)
            self.mget_btn.configure(state=tk.NORMAL)
            self.mput_btn.configure(state=tk.NORMAL)
            self.putdir_btn.configure(state=tk.NORMAL)
            self.getdir_btn.configure(state=tk.NORMAL)

        else:
            self.status_var.set("Chưa kết nối")
            self.status_label.configure(foreground="red")

            # Disable các nút
            self.disconnect_btn.configure(state=tk.DISABLED)
            self.refresh_remote_btn.configure(state=tk.DISABLED)
            self.create_folder_btn.configure(state=tk.DISABLED)
            self.delete_remote_btn.configure(state=tk.DISABLED)
            self.rename_remote_btn.configure(state=tk.DISABLED)
            self.upload_btn.configure(state=tk.DISABLED)
            self.download_btn.configure(state=tk.DISABLED)
            self.mget_btn.configure(state=tk.DISABLED)
            self.mput_btn.configure(state=tk.DISABLED)
            self.putdir_btn.configure(state=tk.DISABLED)
            self.getdir_btn.configure(state=tk.DISABLED)

    def update_remote_files(self):
        """Cập nhật danh sách file remote"""
        if not self.connected:
            return

        def update_thread():
            try:
                self.remote_tree.delete(*self.remote_tree.get_children())
                files = []
                self.ftp_cmd.dir(files.append)
                
                if self.current_remote_dir not in ("/", ""):
                    self.remote_tree.insert("", tk.END, text="📁 /..", values=("", ""))

                for line in files:
                    parts = line.split(maxsplit=8)
                    if len(parts) < 9:
                        continue

                    permissions = parts[0]
                    size = parts[4] if not permissions.startswith('d') else ""
                    name = parts[8]

                    if name in (".", ".."):
                        continue

                    if permissions.startswith('d'):
                        self.remote_tree.insert("", tk.END, text=f"📁 {name}", values=("", ""))
                    else:
                        self.remote_tree.insert("", tk.END, text=f"📄 {name}", values=(f"{size} bytes", ""))

                self.current_remote_dir = self.ftp_cmd.pwd() or "/"
                self.remote_path_var.set(self.current_remote_dir)
            except Exception as e:
                self.log_message(f"Lỗi đọc thư mục remote: {str(e)}", "ERROR")

        threading.Thread(target=update_thread, daemon=True).start()

    def rename_remote_item(self):
        """Đổi tên file/thư mục từ xa"""
        selection = self.remote_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn file/thư mục để đổi tên")
            return

        item = self.remote_tree.item(selection[0])
        old_name = item['text'].replace('📁 ', '').replace('📄 ', '')
        new_name = simpledialog.askstring("Đổi tên", f"Nhập tên mới cho '{old_name}':")
        if not new_name:
            return

        try:
            self.ftp_cmd.rename(old_name, new_name)
            self.log_message(f"Đã đổi tên: {old_name} thành {new_name}")
            self.update_remote_files()
        except Exception as e:
            error_msg = f"Lỗi đổi tên: {str(e)}"
            self.log_message(error_msg, "ERROR")
            messagebox.showerror("Lỗi", error_msg)

    def delete_remote_item(self):
        """Xóa file/thư mục từ xa"""
        selection = self.remote_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn file/thư mục để xóa")
            return

        item = self.remote_tree.item(selection[0])
        name = item['text'].replace('📁 ', '').replace('📄 ', '')
        is_dir = '📁' in item['text']

        if not messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa {'thư mục' if is_dir else 'file'} '{name}'?"):
            return

        try:
            if is_dir:
                self.delete_remote_dir_recursive(name)
            else:
                self.ftp_cmd.delete(name)
            self.log_message(f"Đã xóa {'thư mục' if is_dir else 'file'}: {name}")
            self.update_remote_files()
        except Exception as e:
            error_msg = f"Lỗi xóa {'thư mục' if is_dir else 'file'}: {str(e)}"
            self.log_message(error_msg, "ERROR")
            messagebox.showerror("Lỗi", error_msg)

    def create_remote_folder(self):
        """Tạo thư mục mới trên server"""
        if not self.connected:
            return

        folder_name = simpledialog.askstring("Tạo thư mục", "Nhập tên thư mục:")
        if folder_name:
            try:
                self.ftp_cmd.mkd(folder_name)
                self.log_message(f"Đã tạo thư mục: {folder_name}")
                self.update_remote_files()
            except Exception as e:
                error_msg = f"Lỗi tạo thư mục: {str(e)}"
                self.log_message(error_msg, "ERROR")
                messagebox.showerror("Lỗi", error_msg)

    def clear_log(self):
        """Xóa log"""
        if hasattr(self, "log_text"):
            self.log_text.delete(1.0, tk.END)

    def on_local_double_click(self, event):
        selected = self.local_tree.selection()
        if not selected:
            return

        item = self.local_tree.item(selected[0])
        name = item['text']

        if name == "📁 /..":
            self.current_local_dir = os.path.dirname(self.current_local_dir)
            self.local_path_var.set(self.current_local_dir)
            self.update_local_files()
            self.log_message(f"Đã quay lại thư mục cha local: {self.current_local_dir}")
            return

        if name.startswith("📁 "):
            folder_name = name.replace("📁 ", "")
            new_path = os.path.join(self.current_local_dir, folder_name)
            if os.path.isdir(new_path):
                self.current_local_dir = new_path
                self.local_path_var.set(self.current_local_dir)
                self.update_local_files()
                self.log_message(f"Đã chuyển vào thư mục local: {self.current_local_dir}")

    def on_remote_double_click(self, event):
        """Xử lý double-click thư mục trong remote_tree"""
        selected = self.remote_tree.selection()
        if not selected:
            return

        item = self.remote_tree.item(selected[0])
        name = item['text']

        if name == "📁 /..":
            try:
                self.ftp_cmd.cwd("..")
                self.current_remote_dir = self.ftp_cmd.pwd()
                self.remote_path_var.set(self.current_remote_dir)
                self.log_message(f"Đã quay lại thư mục cha: {self.current_remote_dir}")
                self.update_remote_files()
            except Exception as e:
                self.log_message(f"Lỗi khi quay lại thư mục cha: {e}", "ERROR")
            return

        # Chỉ xử lý nếu là thư mục
        if not name.startswith("📁 "):
            return

        folder_name = name.replace("📁 ", "")
        try:
            self.ftp_cmd.cwd(folder_name)
            self.current_remote_dir = self.ftp_cmd.pwd()
            self.remote_path_var.set(self.current_remote_dir)
            self.log_message(f"Đã chuyển vào thư mục: {self.current_remote_dir}")
            self.update_remote_files()
        except Exception as e:
            self.log_message(f"Lỗi cd: {str(e)}", "ERROR")
            messagebox.showerror("Lỗi", f"Không thể chuyển vào thư mục: {folder_name}")

    def on_remote_path_enter(self, event):
        path = self.remote_path_var.get()
        try:
            self.ftp_cmd.cwd(path)
            self.current_remote_dir = self.ftp_cmd.pwd()
            self.remote_path_var.set(self.current_remote_dir)
            self.update_remote_files()
            self.log_message(f"Đã chuyển đến thư mục: {self.current_remote_dir}")
        except Exception as e:
            self.log_message(f"Lỗi khi chuyển đến thư mục: {e}", "ERROR")
            messagebox.showerror("Lỗi", f"Không thể chuyển đến: {path}")

    # ================== Các lệnh FTP ==================

    def do_ascii(self):
        """Chuyển chế độ truyền file sang ASCII (text mode)"""
        if not self.connected: 
            messagebox.showerror("Error", "Not connected to FTP server")
            return
        self.ftp_cmd.voidcmd("TYPE A")
        self.transfer_mode = 'ascii'
        self.log_message("Switched to ASCII mode.")

    def do_binary(self):
        """Chuyển chế độ truyền file sang binary (dạng nhị phân)"""
        if not self.connected:
            messagebox.showerror("Error", "Not connected to FTP server")
            return
        self.ftp_cmd.voidcmd("TYPE I")
        self.transfer_mode = 'binary'
        self.log_message("Switched to Binary mode.")

    def do_status(self):
        """Hiển thị trạng thái kết nối hiện tại và các chế độ truyền"""
        status_msg = []
        if self.connected:
            status_msg.append("Connection status: Connected.")
            status_msg.append(f"Host: {self.ftp.host}, Port: {self.ftp.port}")
            status_msg.append(f"Current local directory: {self.current_local_dir}")
            try:
                status_msg.append(f"Current FTP directory: {self.ftp.pwd()}")
            except all_errors:
                status_msg.append("Unable to retrieve the current FTP directory (possibly due to connection error).")
        else: 
            status_msg.append("Connection status: Not connected.")
        
        mode = 'ON' if self.prompt_on_mget_mput else 'OFF'
        status_msg.append(f"Confirmation mode (prompt) for mget/mput: {mode}")
        status_msg.append(f"File transfer mode: {self.transfer_mode}")
        status_msg.append(f"Passive FTP mode: {'ON' if self.passive_mode else 'OFF'}")
        
        messagebox.showinfo("Status", "\n".join(status_msg))

    def do_passive(self):
        """Bật/tắt chế độ passive FTP"""
        self.passive_mode = not self.passive_mode
        status = "ON" if self.passive_mode else "OFF"
        self.log_message(f"Passive FTP mode: {status}.")
        if self.connected:
            self.ftp_cmd.set_pasv(self.passive_mode)

    def do_prompt(self):
        """Bật/tắt chế độ xác nhận khi dùng mget hoặc mput"""
        self.prompt_on_mget_mput = not self.prompt_on_mget_mput
        status = "ON" if self.prompt_on_mget_mput else "OFF"
        self.log_message(f"Confirmation mode (prompt) has been {status}.")

    def do_lcd(self, path=None):
        """Thay đổi thư mục làm việc hiện tại của máy cục bộ"""
        if path is None:
            path = simpledialog.askstring("Change Local Directory", "Enter local directory path:")
            if not path:
                return

        try:
            os.chdir(path)
            self.current_local_dir = os.getcwd()
            self.local_path_var.set(self.current_local_dir)
            self.log_message(f"Moved to local directory: {self.current_local_dir}")
            self.update_local_files()
        except OSError as e:
            self.log_message(f"Error: Unable to change local directory: {e}", "ERROR")
            messagebox.showerror("Error", f"Unable to change local directory: {e}")

    def do_get(self):
        """Tải về 1 file từ FTP server về máy cục bộ"""
        selection = self.remote_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a file to download")
            return

        item = self.remote_tree.item(selection[0])
        if '📁' in item['text']:
            messagebox.showwarning("Warning", "Please select a file, not a directory")
            return

        remote_file = item['text'].replace('📄 ', '')
        local_file = filedialog.asksaveasfilename(
            initialdir=self.current_local_dir,
            initialfile=os.path.basename(remote_file),
            title="Save file as"
        )
        
        if not local_file:
            return

        os.makedirs(Config.DOWNLOAD_DIR, exist_ok=True)

        # Tạo progress window
        progress_window = ProgressWindow(self.root, f"Downloading {os.path.basename(remote_file)}")

        def download_thread():
            try:
                # Lấy kích thước file từ xa
                total_size = 0
                try:
                    total_size = self.ftp_cmd.size(remote_file)
                except Exception as e:
                    self.log_message(f"Could not get size of remote file {remote_file}: {e}", "WARNING")

                def progress_callback(transferred, total_size):
                    if progress_window.is_cancelled:
                        return
                    percent = (transferred / total_size) * 100 if total_size else 0
                    progress_window.window.after(0, lambda p=percent, st=f"Đang download: {os.path.basename(remote_file)} ({percent:.1f}%)": progress_window.update_progress(p, st))

                self.log_message(f"Đang download {remote_file}...")
                if self.ftp_helpers._download_file(remote_file, local_file, self.transfer_mode, progress_callback=progress_callback):
                    self.log_message(f"Successfully downloaded {remote_file} to {local_file}")
                    messagebox.showinfo("Success", f"Successfully downloaded {remote_file}")
                    self.update_local_files()
                else:
                    self.log_message(f"Cannot download file {remote_file}", "ERROR")
                    messagebox.showerror("Error", f"Cannot download file {remote_file}")
            except Exception as e:
                self.log_message(f"Lỗi download: {str(e)}", "ERROR")
            finally:
                if not progress_window.is_cancelled:
                    self.root.after(0, progress_window.close)

        threading.Thread(target=download_thread, daemon=True).start()

    def do_mget(self):
        """Tải về nhiều file từ FTP server, hỗ trợ chọn nhiều file"""
        # Lấy danh sách các file từ xa để người dùng chọn
        try:
            all_remote_files = self.ftp_cmd.nlst()
            if all_remote_files is None:
                messagebox.showinfo("Info", "Không có file nào trên server để tải xuống.")
                return
        except Exception as e:
            self.log_message(f"Error getting remote file list: {e}", "ERROR")
            messagebox.showerror("Error", f"Error getting remote file list: {e}")
            return

        # Tạo một cửa sổ tạm thời để hiển thị danh sách file và cho phép chọn
        selection_window = tk.Toplevel(self.root)
        selection_window.title("Chọn file để tải xuống")
        selection_window.geometry("600x400")
        selection_window.transient(self.root)
        selection_window.grab_set()

        listbox_frame = tk.Frame(selection_window)
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        file_listbox = tk.Listbox(listbox_frame, selectmode=tk.MULTIPLE, yscrollcommand=scrollbar.set)
        for f in all_remote_files:
            file_listbox.insert(tk.END, f)
        file_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=file_listbox.yview)

        selected_files = []
        def on_select():
            for i in file_listbox.curselection():
                selected_files.append(file_listbox.get(i))
            selection_window.destroy()

        select_button = tk.Button(selection_window, text="Chọn", command=on_select)
        select_button.pack(pady=5)

        self.root.wait_window(selection_window)

        if not selected_files:
            self.log_message("Không có file nào được chọn để tải xuống.")
            return

        dest_dir = filedialog.askdirectory(
            initialdir=self.current_local_dir,
            title="Chọn thư mục lưu file tải xuống"
        )
        if not dest_dir:
            return

        os.makedirs(dest_dir, exist_ok=True)
        download_count = 0
        total_files_to_download = len(selected_files)
        total_bytes_to_transfer = 0

        # Tính tổng kích thước file trong luồng phụ
        progress_window = ProgressWindow(self.root, f"Downloading {total_files_to_download} file(s)")

        def mget_thread():
            nonlocal download_count
            bytes_transferred_overall = 0
            
            # Tính tổng kích thước file
            current_total_bytes = 0
            for remote_file in selected_files:
                try:
                    current_total_bytes += self.ftp_cmd.size(remote_file)
                except Exception as e:
                    self.log_message(f"Could not get size of remote file {remote_file}: {e}", "WARNING")
                    pass
            
            if current_total_bytes == 0 and total_files_to_download > 0:
                self.log_message("Warning: Total size of selected files is 0 or could not be determined.", "WARNING")

            try:
                for i, remote_file in enumerate(selected_files):
                    if progress_window.is_cancelled:
                        self.log_message("Mget cancelled by user.")
                        break

                    local_file = os.path.join(dest_dir, os.path.basename(remote_file))

                    total_file_size = 0
                    try:
                        total_file_size = self.ftp_cmd.size(remote_file)
                    except Exception as e:
                        self.log_message(f"Could not get size of remote file {remote_file}: {e}", "WARNING")

                    last_transferred = 0
                    def progress_callback(transferred, total=None):
                        if progress_window.is_cancelled:
                            return
                        nonlocal bytes_transferred_overall, last_transferred
                        file_percent = (transferred / total_file_size) * 100 if total_file_size else 0
                        delta = transferred - last_transferred
                        bytes_transferred_overall += delta
                        last_transferred = transferred
                        overall_percent = (bytes_transferred_overall / current_total_bytes) * 100 if current_total_bytes else 0
                        self.root.after(0, lambda p=overall_percent, st=f"Downloading {i+1}/{total_files_to_download}: {os.path.basename(remote_file)} ({file_percent:.1f}%)": progress_window.update_progress(min(p, 100), st))

                    if self.ftp_helpers._download_file(remote_file, local_file, self.transfer_mode, progress_callback=progress_callback):
                        self.log_message(f"Successfully downloaded {remote_file}.")
                        download_count += 1
                    else:
                        self.log_message(f"Unable to download {remote_file}.", "ERROR")

                self.log_message(f"mget complete. Downloaded {download_count} file(s).")
                self.root.after(0, lambda: messagebox.showinfo("Complete", f"Downloaded {download_count} file(s)"))
                self.root.after(0, self.update_local_files)
            except Exception as e:
                self.log_message(f"Error executing mget command: {e}", "ERROR")
                self.root.after(0, lambda err=e: messagebox.showerror("Error", f"Error executing mget command: {err}"))
            finally:
                if not progress_window.is_cancelled:
                    self.root.after(0, progress_window.close)

        threading.Thread(target=mget_thread, daemon=True).start()

    def do_put(self):
        """Tải 1 file từ máy cục bộ lên FTP server (phải qua quét virus trước)"""
        local_file = filedialog.askopenfilename(
            initialdir=self.current_local_dir,
            title="Select file to upload"
        )
        if not local_file:
            return

        remote_file = simpledialog.askstring(
            "Upload", 
            f"Enter remote filename (leave blank for '{os.path.basename(local_file)}'):",
            initialvalue=os.path.basename(local_file)
        ) or os.path.basename(local_file)

        if not os.path.exists(local_file):
            self.log_message(f"Error: Local file '{local_file}' not exist.", "ERROR")
            messagebox.showerror("Error", f"Local file '{local_file}' not exist.")
            return

        # Tạo progress window
        progress_window = ProgressWindow(self.root, f"Uploading {os.path.basename(local_file)}")

        def upload_thread():
            try:
                self.log_message(f"Scanning for viruses in file {local_file}...")
                progress_window.window.after(0, lambda: progress_window.update_progress(10, f"Đang quét virus: {os.path.basename(local_file)}"))

                is_clean, message = self.virus_scanner.scan_file(local_file)

                if is_clean:
                    self.log_message(f"File {local_file} clean. Uploading...")

                    def progress_callback(transferred, total):
                        if progress_window.is_cancelled:
                            return
                        percent = (transferred / total) * 100 if total else 0
                        progress_window.window.after(0, lambda p=percent: progress_window.update_progress(p, f"Đang upload: {p:.1f}%"))

                    progress_window.window.after(0, lambda: progress_window.update_progress(20, "Bắt đầu upload..."))

                    if self.ftp_helpers._upload_file(local_file, remote_file, self.transfer_mode, progress_callback=progress_callback):
                        self.log_message(f"Successfully uploaded {local_file} to {remote_file}.")
                        messagebox.showinfo("Success", f"Successfully uploaded {local_file}")
                        self.update_remote_files()
                    else:
                        self.log_message(f"Unable to upload {local_file}.", "ERROR")
                        messagebox.showerror("Error", f"Unable to upload {local_file}")
                else:
                    self.log_message(f"Warning: {message} Upload canceled.", "WARNING")
                    messagebox.showwarning("Warning", f"{message}\nUpload canceled.")
            except Exception as e:
                self.log_message(f"Lỗi upload: {str(e)}", "ERROR")
            finally:
                if not progress_window.is_cancelled:
                    self.root.after(0, progress_window.close)

        threading.Thread(target=upload_thread, daemon=True).start()

    def do_mput(self):
        """Tải nhiều file từ máy cục bộ lên FTP server, quét hết trước khi upload"""
        local_files = filedialog.askopenfilenames(
            initialdir=self.current_local_dir,
            title="Select files to upload",
            multiple=True
        )
        if not local_files:
            return
        
        def mput_thread():
            # Lấy tổng kích thước file và quét virus trong luồng phụ
            total_files_to_upload = len(local_files)
            clean_files = []
            total_bytes_to_transfer = 0

            # Tạo progress window trước khi quét virus
            progress_window = ProgressWindow(self.root, f"Scanning and Uploading {total_files_to_upload} file(s)")

            try:
                self.log_message("Scanning selected files for viruses...")
                progress_window.window.after(0, lambda: progress_window.update_progress(0, "Đang quét virus..."))

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future_to_file = {executor.submit(self.virus_scanner.scan_file, f): f for f in local_files}
                    for i, future in enumerate(concurrent.futures.as_completed(future_to_file)):
                        local_file = future_to_file[future]
                        try:
                            is_clean, message = future.result()
                            if is_clean:
                                clean_files.append(local_file)
                                total_bytes_to_transfer += os.path.getsize(local_file)
                            else:
                                self.log_message(f"Warning: File {local_file} - {message}. Will not upload.", "WARNING")
                                self.root.after(0, lambda lf=local_file, msg=message: messagebox.showwarning("Warning", f"File {os.path.basename(lf)} - {msg}\nWill not upload."))
                        except Exception as exc:
                            self.log_message(f"File {local_file} generated an exception during scan: {exc}", "ERROR")
                            self.root.after(0, lambda lf=local_file, e=exc: messagebox.showerror("Error", f"Error scanning file {os.path.basename(lf)}: {e}"))
                        
                        # Cập nhật tiến trình quét virus
                        scan_percent = ((i + 1) / total_files_to_upload) * 100 * 0.2 # 20% cho quét virus
                        progress_window.window.after(0, lambda p=scan_percent: progress_window.update_progress(p, f"Đang quét virus ({i+1}/{total_files_to_upload})..."))

                if not clean_files:
                    self.log_message("No clean files available for upload.")
                    self.root.after(0, lambda: messagebox.showinfo("Info", "No clean files available for upload"))
                    progress_window.window.after(0, progress_window.close)
                    return
                
                upload_count = 0
                bytes_transferred_overall = 0
                for i, local_file in enumerate(clean_files):
                    if progress_window.is_cancelled:
                        self.log_message("Mput cancelled by user.")
                        break

                    remote_file = os.path.basename(local_file)
                    total_file_size = os.path.getsize(local_file)
                    last_transferred = [0]  # để tính delta

                    def progress_callback(transferred, total):
                        if progress_window.is_cancelled:
                            return
                        nonlocal bytes_transferred_overall
                        delta = transferred - last_transferred[0]
                        last_transferred[0] = transferred
                        bytes_transferred_overall += delta

                        file_percent = (transferred / total_file_size) * 100 if total_file_size else 0
                        # Tổng tiến trình: 20% cho quét virus, 80% cho upload
                        overall_percent = 20 + (bytes_transferred_overall / total_bytes_to_transfer) * 80 if total_bytes_to_transfer else 20
                        self.root.after(0, lambda: progress_window.update_progress(
                            min(overall_percent, 100),
                            f"Uploading {i+1}/{len(clean_files)}: {os.path.basename(local_file)} ({file_percent:.1f}%)"))
                    
                    if self.ftp_helpers._upload_file(local_file, remote_file, self.transfer_mode, progress_callback=progress_callback):
                        self.log_message(f"Successfully uploaded {local_file} to {remote_file}")
                        upload_count += 1
                    else:
                        self.log_message(f"Unable to upload {local_file}", "ERROR")

                self.log_message(f"Upload complete. Uploaded {upload_count} file(s).")
                self.root.after(0, lambda: messagebox.showinfo("Complete", f"Uploaded {upload_count} file(s)"))
                self.root.after(0, self.update_remote_files)
            except Exception as e:
                self.log_message(f"Error executing mput command: {e}", "ERROR")
                self.root.after(0, lambda err=e: messagebox.showerror("Error", f"Error executing mput command: {err}"))
            finally:
                if not progress_window.is_cancelled:
                    self.root.after(0, progress_window.close)

        threading.Thread(target=mput_thread, daemon=True).start()

    def do_cd(self, path=None):
        """Thay đổi thư mục hiện tại trên FTP server"""
        if not self.connected:
            messagebox.showerror("Error", "Not connected to FTP server")
            return

        if path is None:
            path = simpledialog.askstring("Change Directory", "Enter remote directory path:")
            if not path:
                return

        resp = self.ftp_cmd.cwd(path)
        if resp:
            self.current_remote_dir = self.ftp_cmd.pwd()
            self.remote_path_var.set(self.current_remote_dir)
            self.log_message(f"Changed to directory: {self.current_remote_dir}")

            self.update_remote_files()

    def do_pwd(self):
        """In ra thư mục hiện tại trên FTP server"""
        if not self.connected:
            messagebox.showerror("Error", "Not connected to FTP server")
            return

        remote_dir = self.ftp_cmd.pwd()
        if remote_dir:
            self.current_remote_dir = remote_dir
            self.remote_path_var.set(self.current_remote_dir)
            messagebox.showinfo("Current Directory", f"Current directory on FTP server: {self.current_remote_dir}")

    def do_putdir(self):
        """Tải lên toàn bộ một thư mục và các thư mục con lên FTP server (recursive upload)"""
        if not self.connected:
            messagebox.showerror("Error", "Not connected to FTP server")
            return

        local_dir = filedialog.askdirectory(
            initialdir=self.current_local_dir,
            title="Select directory to upload"
        )
        if not local_dir:
            return

        remote_dir = simpledialog.askstring(
            "Upload Directory", 
            f"Enter remote directory name (leave blank for \'{os.path.basename(local_dir)}\'):",
            initialvalue=os.path.basename(local_dir)
        ) or os.path.basename(local_dir)

        if not os.path.isdir(local_dir):
            messagebox.showerror("Error", f"Local directory \'{local_dir}\' does not exist or is not a directory")
            return

        self.log_message(f"Uploading directory {local_dir} to {remote_dir}...")

        progress_window = ProgressWindow(self.root, f"Uploading directory {os.path.basename(local_dir)}")

        def putdir_thread():
            try:
                # Tính tổng số file và thư mục để ước tính tiến trình
                total_items = 0
                for root, dirs, files in os.walk(local_dir):
                    total_items += len(dirs) + len(files)
                
                processed_items = [0] # Sử dụng list để có thể thay đổi trong hàm lồng

                def progress_callback_recursive(current_item_path, is_dir=False):
                    processed_items[0] += 1
                    percent = (processed_items[0] / total_items) * 100 if total_items else 0
                    item_name = os.path.basename(current_item_path)
                    status_text = f"Processing {'directory' if is_dir else 'file'}: {item_name} ({processed_items[0]}/{total_items})"
                    self.root.after(0, lambda p=percent, st=status_text: progress_window.update_progress(p, st))

                self._recursive_upload(local_dir, remote_dir, progress_window, progress_callback_recursive)
                if not progress_window.is_cancelled:
                    self.log_message(f"Upload of directory {local_dir} completed.")
                    self.root.after(0, lambda: messagebox.showinfo("Success", f"Directory {local_dir} uploaded successfully"))
                    self.root.after(0, self.update_remote_files)
                else:
                    self.log_message("Upload directory cancelled by user.")
            except Exception as e:
                self.log_message(f"Error uploading directory: {str(e)}", "ERROR")
                self.root.after(0, lambda err=e: messagebox.showerror("Error", f"Error uploading directory: {str(err)}"))
            finally:
                if not progress_window.is_cancelled:
                    self.root.after(0, progress_window.close)

        threading.Thread(target=putdir_thread, daemon=True).start()

    def _recursive_upload(self, local_path, remote_path, progress_window, progress_callback_recursive):
        """Hàm hỗ trợ tải lên thư mục đệ quy"""
        if progress_window.is_cancelled:
            return

        progress_callback_recursive(local_path, is_dir=True)

        try:
            self.ftp_cmd.mkd(remote_path)
        except all_errors as e:
            if "File exists" not in str(e):
                raise

        original_ftp_dir = self.ftp_cmd.pwd()
        self.ftp_cmd.cwd(remote_path)

        self.log_message(f"Scanning and uploading files in {local_path}...")
        for item in os.listdir(local_path):
            if progress_window.is_cancelled:
                break

            local_item_path = os.path.join(local_path, item)
            remote_item_path = item

            if os.path.isfile(local_item_path):
                progress_callback_recursive(local_item_path)
                is_clean, message = self.virus_scanner.scan_file(local_item_path)
                if is_clean:
                    if self.ftp_helpers._upload_file(local_item_path, remote_item_path, self.transfer_mode):
                        self.log_message(f"  Successfully uploaded {item}")
                    else:
                        self.log_message(f"  Unable to upload {item}", "ERROR")
                else:
                    self.log_message(f"  Warning: File {item} - {message}. Will not upload.", "WARNING")  
            elif os.path.isdir(local_item_path):
                self.log_message(f"  Processing subdirectory: {local_item_path}")
                self._recursive_upload(local_item_path, remote_item_path, progress_window, progress_callback_recursive)

        self.ftp_cmd.cwd(original_ftp_dir)

    def do_getdir(self):
        """Tải về toàn bộ một thư mục và các thư mục con từ FTP server (recursive download)"""
        if not self.connected:
            messagebox.showerror("Error", "Not connected to FTP server")
            return

        remote_dir = simpledialog.askstring(
            "Download Directory", 
            "Enter remote directory path to download:"
        )
        if not remote_dir:
            return

        local_dir = filedialog.askdirectory(
            initialdir=self.current_local_dir,
            title="Select destination directory"
        )
        if not local_dir:
            return

        self.log_message(f"Downloading directory {remote_dir} to {local_dir}...")  
        
        progress_window = ProgressWindow(self.root, f"Downloading directory {os.path.basename(remote_dir)}")

        def getdir_thread():
            try:
                # Tính tổng số file và thư mục để ước tính tiến trình
                total_items = [0] # Sử dụng list để có thể thay đổi trong hàm lồng
                # Hàm đệ quy để đếm số lượng file và thư mục
                def count_remote_items(path):
                    try:
                        self.ftp_cmd.cwd(path)
                        items = []
                        self.ftp_cmd.dir(items.append)
                        for line in items:
                            parts = line.split(maxsplit=8)
                            if len(parts) < 9:
                                continue
                            name = parts[8]
                            permissions = parts[0]
                            if name in (".", ".."):
                                continue
                            total_items[0] += 1
                            if permissions.startswith('d'):
                                count_remote_items(name)
                    except Exception as e:
                        self.log_message(f"Error counting remote items in {path}: {e}", "WARNING")
                    finally:
                        self.ftp_cmd.cwd("..") # Quay lại thư mục cha sau khi đếm xong

                original_ftp_dir = self.ftp_cmd.pwd()
                count_remote_items(remote_dir)
                self.ftp_cmd.cwd(original_ftp_dir) # Quay lại thư mục ban đầu

                processed_items = [0] # Sử dụng list để có thể thay đổi trong hàm lồng

                def progress_callback_recursive(current_item_path, is_dir=False):
                    processed_items[0] += 1
                    percent = (processed_items[0] / total_items[0]) * 100 if total_items[0] else 0
                    item_name = os.path.basename(current_item_path)
                    item_type = "directory" if is_dir else "file"
                    status_text = f"Processing {item_type}: {item_name} ({processed_items[0]}/{total_items[0]})"
                    self.root.after(0, lambda p=percent, st=status_text: progress_window.update_progress(p, st))

                self._recursive_download(remote_dir, local_dir, progress_window, progress_callback_recursive)
                if not progress_window.is_cancelled:
                    self.log_message(f"Download of directory {remote_dir} completed.")
                    self.root.after(0, lambda: messagebox.showinfo("Success", f"Directory {remote_dir} downloaded successfully"))
                    self.root.after(0, self.update_local_files)
                else:
                    self.log_message("Download directory cancelled by user.")
            except Exception as e:
                self.log_message(f"Error downloading directory: {str(e)}", "ERROR")
                self.root.after(0, lambda err=e: messagebox.showerror("Error", f"Error downloading directory: {str(err)}"))
            finally:
                if not progress_window.is_cancelled:
                    self.root.after(0, progress_window.close)

        threading.Thread(target=getdir_thread, daemon=True).start()

    def _recursive_download(self, remote_path, local_path, progress_window, progress_callback_recursive):
        """Hàm hỗ trợ tải xuống thư mục đệ quy"""
        if progress_window.is_cancelled:
            return

        os.makedirs(local_path, exist_ok=True)
        original_ftp_dir = self.ftp_cmd.pwd()

        try:
            self.ftp_cmd.cwd(remote_path)
        except all_errors as e:
            raise Exception(f"Unable to access remote directory {remote_path}: {e}")

        items = []
        self.ftp_cmd.dir(items.append) 

        for line in items:
            if progress_window.is_cancelled:
                break

            parts = line.split(maxsplit=8)
            if len(parts) < 9:
                continue
            
            permissions = parts[0]
            item_name = parts[8]

            if item_name in (".", ".."): 
                continue

            remote_item_path = item_name
            local_item_path = os.path.join(local_path, item_name)

            if permissions.startswith("d"):
                progress_callback_recursive(local_item_path, is_dir=True)
                self.log_message(f"  Processing subdirectory: {remote_item_path}")
                self._recursive_download(remote_item_path, local_item_path, progress_window, progress_callback_recursive)
            else:
                progress_callback_recursive(local_item_path)
                self.log_message(f"  Downloading file: {remote_item_path}")
                if self.ftp_helpers._download_file(remote_item_path, local_item_path, self.transfer_mode):
                    self.log_message(f"  Successfully downloaded {item_name}")
                else:
                    self.log_message(f"  Unable to download {item_name}", "ERROR")
        
        self.ftp_cmd.cwd(original_ftp_dir)

    def do_quit(self):
        """Thoát khỏi chương trình client"""
        if messagebox.askyesno("Quit", "Are you sure you want to quit?"):
            self.log_message("Exiting FTP Client.")
            if self.connected:
                self.disconnect_ftp()
            self.root.destroy()

    def do_ls(self, path=None):
        """Liệt kê các file và thư mục trên FTP server"""
        if not self.connected:
            messagebox.showerror("Error", "Not connected to FTP server")
            return

        if path is None:
            path = simpledialog.askstring("List Directory", "Enter remote directory path (leave blank for current):")
            if path is None:  # User pressed Cancel
                return

        path = path or "."
        self.log_message(f"Listing directory: {path}")
        
        try:
            files = []
            self.ftp_cmd.dir(path, files.append)
            
            # Hiển thị kết quả trong một cửa sổ mới
            result_window = tk.Toplevel(self.root)
            result_window.title(f"Directory Listing - {path}")
            
            text = tk.Text(result_window, wrap=tk.WORD)
            scroll = ttk.Scrollbar(result_window, command=text.yview)
            text.configure(yscrollcommand=scroll.set)
            
            text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scroll.pack(side=tk.RIGHT, fill=tk.Y)
            
            for line in files:
                text.insert(tk.END, line + "\n")
                
            text.configure(state=tk.DISABLED)
            
        except Exception as e:
            self.log_message(f"Error listing directory: {str(e)}", "ERROR")
            messagebox.showerror("Error", f"Error listing directory: {str(e)}")

    def do_lls(self, path=None):
        """Liệt kê các file và thư mục trong thư mục hiện tại của máy cục bộ"""
        if path is None:
            path = simpledialog.askstring("List Local Directory", "Enter local directory path (leave blank for current):")
            if path is None:  # User pressed Cancel
                return

        path = path or self.current_local_dir
        self.log_message(f"Listing local directory: {path}")
        
        try:
            files = os.listdir(path)
            
            # Hiển thị kết quả trong một cửa sổ mới
            result_window = tk.Toplevel(self.root)
            result_window.title(f"Local Directory Listing - {path}")
            
            text = tk.Text(result_window, wrap=tk.WORD)
            scroll = ttk.Scrollbar(result_window, command=text.yview)
            text.configure(yscrollcommand=scroll.set)
            
            text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scroll.pack(side=tk.RIGHT, fill=tk.Y)
            
            for file in files:
                full_path = os.path.join(path, file)
                if os.path.isdir(full_path):
                    text.insert(tk.END, f"<DIR> {file}\n")
                else:
                    size = os.path.getsize(full_path)
                    text.insert(tk.END, f"{size:>10} {file}\n")
            
            text.insert(tk.END, f"\nTotal: {len(files)} items")
            text.configure(state=tk.DISABLED)
            
        except Exception as e:
            self.log_message(f"Error listing local directory: {str(e)}", "ERROR")
            messagebox.showerror("Error", f"Error listing local directory: {str(e)}")

    def do_lpwd(self):
        """Hiển thị thư mục làm việc hiện tại của máy cục bộ"""
        self.current_local_dir = os.getcwd()
        self.local_path_var.set(self.current_local_dir)
        messagebox.showinfo("Local Directory", f"Local directory: {self.current_local_dir}")

    def do_rmdir(self):
        """Xóa thư mục (rỗng) trên FTP server"""
        if not self.connected:
            messagebox.showerror("Error", "Not connected to FTP server")
            return

        dir_name = simpledialog.askstring("Remove Directory", "Enter directory name to remove:")
        if not dir_name:
            return

        if not messagebox.askyesno("Confirm", f"Are you sure you want to remove directory '{dir_name}'?"):
            return

        try:
            resp = self.ftp_cmd.rmd(dir_name)
            if resp:
                self.log_message(f"Deleted directory: {dir_name}")
                messagebox.showinfo("Success", f"Directory {dir_name} deleted successfully")
                self.update_remote_files()
        except Exception as e:
            self.log_message(f"Error deleting directory: {str(e)}", "ERROR")
            messagebox.showerror("Error", f"Error deleting directory: {str(e)}")

    def delete_remote_dir_recursive(self, path):
        """Xóa thư mục và toàn bộ nội dung bên trong (đệ quy an toàn)"""
        if not self.connected or not self.ftp:
            raise Exception("Chưa kết nối đến FTP server.")

        try:
            # Dùng ftp.dir để phân tích nội dung
            lines = []
            self.ftp_cmd.dir(path, lines.append)

            for line in lines:
                parts = line.split(maxsplit=8)
                if len(parts) < 9:
                    continue

                name = parts[8]
                permissions = parts[0]

                if name in (".", ".."):
                    continue

                full_path = f"{path}/{name}" if not path.endswith("/") else f"{path}{name}"

                if permissions.startswith('d'):
                    self.delete_remote_dir_recursive(full_path)
                else:
                    self.ftp_cmd.delete(full_path)

            # Sau khi xóa hết bên trong, xóa thư mục chính
            self.ftp_cmd.rmd(path)

        except Exception as e:
            # Ghi log nếu còn log_text
            if hasattr(self, "log_text"):
                self.log_message(f"Lỗi khi xóa thư mục {path}: {e}", "ERROR")
            raise e
        
    def do_quit(self):
        """Thoát ứng dụng hoàn toàn"""
        self.log_message("Đã đóng ứng dụng FTP Client.")
        if self.connected:
            self.disconnect_ftp()
        self.root.destroy()
        sys.exit(0)
