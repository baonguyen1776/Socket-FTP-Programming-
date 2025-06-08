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

class FTPCommands(cmd.Cmd): 
    intro = "Welcome to FTP Client. Type help or ? to see available commands.\n"
    prompt = "ftp> "

    def __init__(self):
        super().__init__()
        self.ftp = None
        self.ftp_helpers = None
        self.virus_scanner = VirusScan()
        self.current_local_dir = os.getcwd()
        self.current_ftp_dir = "/"
        self.prompt_on_mget_mput = True
        self.connected = False
        self.passive_mode = True 
        self.transfer_mode = 'binary'

    def precmd(self, line): # Xử lý trước khi thực hiện lệnh
        Utils.log_event(f"User command: {line}", level=logging.DEBUG)
        return line
    
    def postcmd(self, stop, line): # Xử lý sau khi thực hiện lệnh
        return stop
    
    def _ftp_cmd(self, func, *args, **kwargs): #wrapper để thực hiện lệnh FTP và xử lý lỗi chung
        if not self.connected:
            print("Error: Not connected to the FTP server. Please use the \'open\' command.")
            return None
        try: 
            is_data_transfer = func.__name__in (
                'nlst', 'retrbinary', 'retrlines', 'storbinary', 'storlines', 'dir'
            )
            if is_data_transfer:
                self.ftp.set_pasv(self.passive_mode)
                Utils.log_event(f"Set passive mode {self.passive_mode} for {func.__name__}", level=logging.DEBUG)

            return func(*args, **kwargs)
        except error_perm as e:
            print(f"FTP permission error: {e}")
            Utils.log_event(f"FTP permission error: {e}", level=logging.ERROR)
        except error_temp as e:
            print(f"Temporary FTP error: {e}")
            Utils.log_event(f"Temporary FTP error: {e}", level=logging.ERROR)
        except error_proto as e:
            print(f"FTP protocol error: {e}")
            Utils.log_event(f"FTP protocol error: {e}", level=logging.ERROR)
        except all_errors as e:
            print(f"FTP Error: {e}")
            Utils.log_event(f"FTP Error: {e}", level=logging.ERROR)
        except socket.gaierror as e:
            print(f"Network error (address lookup): {e}")
            Utils.log_event(R"Network error (address lookup): {e}", level=logging.ERROR)
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
        Sử dụng: ls [đường_dẫn]"""

        path = args if args else "."
        print(f"Listing directory: {path}")
        self._ftp_cmd(self.ftp.dir, path)

    def do_cd(self, args): 
        """cd: Thay đổi thư mục hiện tại trên FTP server.
        Sử dụng: cd <đường_dẫn>
        """
        if not args: print("Please provide the path."); return
        path = args
        resp = self._ftp_cmd(self.ftp.cwd, path)
        if resp:
            self.current_ftp_dir = self._ftp_cmd(self.ftp.pwd)
            print(f"Moved to directory: {self.current_ftp_dir}")

    def do_pwd(self, args):
        """pwd: In ra thư mục hiện tại trên FTP server.
        Sử dụng: pwd
        """
        remote_dir = self._ftp_cmd(self.ftp.pwd)