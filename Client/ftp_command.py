import cmd
from ftplib import FTP, all_errors, error_perm, error_temp, error_proto
import os
import glob
import socket
from .ftp_helpers import FTPHelpers
from .virus_scan import VirusScan
from .utils import Utils
from .config import Config
import logging

class FtpCommands(cmd.Cmd):
    intro = "Welcome to FTP Client. Type 'help' or '?' to view commands.\n"
    prompt = "ftp> "

    def __init__(self):
        super().__init__()
        self.ftp = None
        self.ftp_helpers = None
        self.virus_scanner = VirusScan()
        self.current_local_dir = os.getcwd()
        self.current_ftp_dir = "/" # Thư mục hiện tại trên FTP server
        self.prompt_on_mget_mput = True
        self.connected = False
        self.passive_mode = True # Mặc định là passive mode
        self.transfer_mode = 'binary' # Mặc định là binary

    def precmd(self, line): # Xử lý trước khi thực hiện lệnh
        Utils.log_event(f"User command: {line}", level=logging.DEBUG)
        return line

    def postcmd(self, stop, line): # Xử lý sau khi thực hiện lệnh
        return stop

    def _ftp_cmd(self, func, *args, **kwargs): # Wrapper để thực hiện lệnh FTP và xử lý lỗi chung
        if not self.connected:
            print("Error: Not connected to FTP server. Please use the \'open\' command.")
            return None
        try:
            # Đảm bảo chế độ passive được đặt đúng trước khi truyền dữ liệu
            is_data_transfer = func.__name__ in (
                'nlst', 'retrbinary', 'retrlines', 'storbinary', 'storlines', 'dir'
            )
            if is_data_transfer:
                self.ftp.set_pasv(self.passive_mode)
                Utils.log_event(f"Set passive mode to {self.passive_mode} for {func.__name__}", level=logging.DEBUG)

            return func(*args, **kwargs)
        except error_perm as e:
            print(f"FTP permission error: {e}")
            Utils.log_event(f"FTP permission error: {e}", level=logging.ERROR)
        except error_temp as e:
            print(f"FTP temporary error: {e}")
            Utils.log_event(f"FTP temporary error: {e}", level=logging.ERROR)
        except error_proto as e:
            print(f"FTP protocol error: {e}")
            Utils.log_event(f"FTP protocol error: {e}", level=logging.ERROR)
        except all_errors as e:
            print(f"FTP error: {e}")
            Utils.log_event(f"FTP error: {e}", level=logging.ERROR)
        except socket.gaierror as e:
            print(f"Network error (address lookup): {e}")
            Utils.log_event(f"Network error (address lookup): {e}", level=logging.ERROR)
            self.connected = False
            self.ftp = None
        except socket.error as e:
            print(f"Network error (socket): {e}")
            Utils.log_event(f"Network error (socket): {e}", level=logging.ERROR)
            self.connected = False
            self.ftp = None
        return None

    def do_ls(self, args):
        """ls: Liệt kê các file và thư mục trên FTP server.
        Sử dụng: ls [đường_dẫn]
        """
        path = args if args else "."
        print(f"Listing directory: {path}")
        self._ftp_cmd(self.ftp.dir, path)

    def do_cd(self, args):
        """cd: Thay đổi thư mục hiện tại trên FTP server.
        Sử dụng: cd <đường_dẫn>
        """
        if not args: print("Please provide a path."); return
        path = args
        resp = self._ftp_cmd(self.ftp.cwd, path)
        if resp:
            self.current_ftp_dir = self._ftp_cmd(self.ftp.pwd)
            print(f"Changed to directory: {self.current_ftp_dir}")

    def do_pwd(self, args): # In ra thư mục hiện tại trên FTP server.
        """pwd: In ra thư mục hiện tại trên FTP server.
        Sử dụng: pwd
        """
        remote_dir = self._ftp_cmd(self.ftp.pwd)
        if remote_dir:
            self.current_ftp_dir = remote_dir
            print(f"Current directory on FTP server: {self.current_ftp_dir}")
    
    def do_mkdir(self, args): # Tạo thư mục mới trên FTP server tại đường dẫn chỉ định.
        """mkdir: Tạo thư mục mới trên FTP server.
        Sử dụng: mkdir <tên_thư_mục>
        """
        if not args: 
            print(f"Please enter name of folder.")
            return
        path = args
        resp = self._ftp_cmd(self.ftp.mkd, path)
        if resp: 
            print(f"Created directory: {resp}")

    def do_rmdir(self, args): # Xóa thư mục (rỗng) trên FTP server.
        """rmdir: Xóa thư mục (rỗng) trên FTP server.
        Sử dụng: rmdir <tên_thư_mục>
        """
        if not args:
            print("Please enter name of folder.") 
            return
        path = args
        resp = self._ftp_cmd(self.ftp.rmd, path)
        if resp:
            print(f"Delete directory: {resp}")

    def do_delete(self, args): # Xóa một file trên FTP server.
        """delete: Xóa một file trên FTP server.
        Sử dụng: delete <tên_file>
        """
        if not args:
            print(f"Please enter name of file.")
            return
        path = args
        resp = self._ftp_cmd(self.ftp.delete, path)
        if resp:
            print(f"Deleted file: {resp}")

    def do_rename(self, args): # Đổi tên một file hoặc thư mục trên FTP server.
        """rename: Đổi tên một file hoặc thư mục trên FTP server.
        Sử dụng: rename <tên_cũ> <tên_mới>
        """
        args = args.split()
        if len(args) != 2:
            print("Use: rename <old_name> <new_name>")
            return
        old_name, new_name = args
        resp = self._ftp_cmd(self.ftp.rename, old_name, new_name)
        if resp:
            print(f"Renamed {old_name} to {new_name}")

    def do_get(self, args): # Tải về 1 file từ FTP server về máy cục bộ.
        """get: Tải về một file từ FTP server.
        Sử dụng: get <tên_file_từ_xa> [tên_file_cục_bộ]
        """
        if not args:
            print("Pleaseenter name of file.")
            return
        args = args.split()
        remote_file = args[0]
        local_file = args[1] if len(args) > 1 else os.path.basename(remote_file)
        local_path = os.path.join(Config.DOWNLOAD_DIR, local_file)

        os.makedirs(Config.DOWNLOAD_DIR, exist_ok=True)

        if self.ftp_helpers._download_file(remote_file, local_file, self.transfer_mode):
            print(f"Successfully downloaded {remote_file} to {local_path}")
        else: 
            print(f"Cannot download file {remote_file}")

    