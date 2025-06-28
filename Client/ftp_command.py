import cmd
from ftplib import FTP, all_errors, error_perm, error_temp, error_proto
import os
import glob
import socket
from ftp_helpers import FTPHelpers
from virus_scan import VirusScan
from utils import Utils
from config import Config
import logging

class FTPCommands(cmd.Cmd):
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

        if self.ftp_helpers._download_file(remote_file, local_path, self.transfer_mode):
            print(f"Successfully downloaded {remote_file} to {local_path}")
        else: 
            print(f"Cannot download file {remote_file}")

    def do_recv(self, args): # Alias (bí danh) cho do_get – hoạt động giống hệt.
        """recv: Alias cho lệnh get.
        Sử dụng: recv <tên_file_từ_xa> [tên_file_cục_bộ]
        """
        self.do_get(args)

    def do_mget(self, args):  # Tải về nhiều file từ FTP server, hỗ trợ wildcard (*).
        """mget: Tải về nhiều file từ FTP server, hỗ trợ wildcard (*).
        Sử dụng: mget <pattern>
        """
        if not args: 
            print(f"Please enter pattern")
            return
        
        pattern = args
        try:
            all_remote_file = self._ftp_cmd(self.ftp.nlst)
            if all_remote_file is None:
                return 
            
            matching_files = []
            import fnmatch
            for f in all_remote_file:
                if fnmatch.fnmatch(f, pattern):
                    matching_files.append(f)

            if not matching_files:
                print(f"No files matched the pattern \'{pattern}\'.")
                return

            os.makedirs(Config.DOWNLOAD_DIR, exist_ok=True)
            download_count = 0

            for remote_file in matching_files:
                local_file = os.path.join(Config.DOWNLOAD_DIR, os.path.basename(remote_file))

                confirm = 'y'
                if self.prompt_on_mget_mput: 
                    confirm = input(f"Download {remote_file} to {local_file}? (y/n/a): ").lower().strip()
                    if confirm == 'a':
                        self.prompt_on_mget_mput = False
                        confirm = 'y'
                    elif confirm != 'y':
                        print(f"Skipped {remote_file}.")
                        continue
                
                if self.ftp_helpers._download_file(remote_file, local_file, self.transfer_mode):
                    print(f"Successfully downloaded {remote_file}.")
                    download_count += 1
                else: 
                    print(f"Unable to download {remote_file}.")
            print(f"mget complete. Downloaded {download_count} file(s).")
        
        except all_errors as e:
            print(f"Error: {e}")
            Utils.log_event(f"Error executing mget command: {e}", level=logging.ERROR)

    def do_put(self, args): # Tải 1 file từ máy cục bộ lên FTP server (phải qua quét virus trước).
        """put: Tải một file từ máy cục bộ lên FTP server (phải qua quét virus trước).
        Sử dụng: put <tên_file_cục_bộ> [tên_file_từ_xa]
        """
        if not args: 
            print("Please provide the local file name.")
            return
        args = args.split()
        local_file = args[0]
        remote_file = args[1] if len(args) > 1 else os.path.basename(local_file)

        if not os.path.exists(local_file):
            print(f"Error: Local file \'{local_file}\' not exist.")
            return

        print(f"Scanning for viruses in file {local_file}...")
        is_clean, message = self.virus_scanner.scan_file(local_file)

        if is_clean:
            print(f"File {local_file} clean. Downloading...")
            if self.ftp_helpers._upload_file(local_file, remote_file, self.transfer_mode):
                print(f"Successfully uploaded {local_file} to {remote_file}.")
            else: 
                print(f"Unable to upload {local_file}.")
        else:
            print(f"Warning: {message} Upload canceled.")
            Utils.log_event(f"Upload of file {local_file} canceled due to virus: {message}.", level=logging.WARNING)

    def do_mput(self, args): # Tải nhiều file từ máy cục bộ lên FTP server, quét hết trước khi upload.
        """mput: Tải nhiều file từ máy cục bộ lên FTP server, quét hết trước khi upload.
        Sử dụng: mput <pattern>
        """
        if not args: 
            print(f"Please enter pattern.")
            return 
        
        local_files = glob.glob(args)
        if not local_files:
            print(f"No files matched the pattern \'{args}\'.")
            return
        
        files_to_upload = []
        for local_file in local_files:
            if os.path.isfile(local_file):
                confirm = 'y'
                if self.prompt_on_mget_mput:
                    confirm - input(f"Download {local_file}? (y/n/a): ").lower().strip()
                    if confirm == 'a':
                        self.prompt_on_mget_mput = False
                        confirm = 'y'
                elif confirm != 'y':
                    files_to_upload.append(local_file)

        if not files_to_upload:
            print("No files selected for upload.")
            return
        
        print("Scanning selected files for viruses...")
        clean_files = []
        for f in files_to_upload:
            is_clean, message = self.virus_scanner.scan_file(f)
            if is_clean:
                clean_files.append(f)
            else: 
                print (f"Warning: File {f} - {message}. Will not upload.")
                Utils.log_event(f"File {f} was not uploaded due to virus: {message}", level=logging.WARNING)


        if not clean_files:
            print("No clean files available for upload.")
            return
        
        print("Downloading clean file...")
        for local_file in clean_files:
            remote_file = os.path.basename(local_file)
            if self.ftp_helpers._upload_file(local_file, remote_file, self.transfer_mode):
                print(f"Successfully uploaded {local_file} to {remote_file}")
            else: 
                print(f"Unable to upload {local_file}")

    def do_prompt(self, args): # Bật/tắt chế độ xác nhận khi dùng mget hoặc mput.
        """prompt: Bật/tắt chế độ xác nhận khi dùng mget hoặc mput.
        Sử dụng: prompt
        """
        self.prompt_on_mget_mput = not self.prompt_on_mget_mput
        status = "ON" if self.prompt_on_mget_mput else "OFF"
        print(f"Confirmation mode (prompt) has been {status}.")

    def not_connected(self): # Thông báo khi chưa kết nối FTP
        print("Not connected to the FTP server. Please use the \'open\' command to connect.")

    def do_ascii(self, args): # Chuyển chế độ truyền file sang ASCII (text mode).
        """ascii: Chuyển chế độ truyền file sang ASCII (text mode).
        Sử dụng: ascii
        """
        if not self.connected: 
            self.not_connected() 
            return
        self._ftp_cmd(self.ftp.voidcmd, "TYPE A")
        self.transfer_mode = 'ascii'
        print("Switched to ASCII mode.")

    def do_binary(self, args): # Chuyển chế độ truyền file sang binary (dạng nhị phân).
        """binary: Chuyển chế độ truyền file sang binary (dạng nhị phân).
        Sử dụng: binary
        """
        if not self.connected:
            self.not_connected()
            return
        self._ftp_cmd(self.ftp.voidcmd, "TYPE I")
        self.transfer_mode = 'binary'
        print("Switched to Binary mode.")

    def do_status(self, args): # Hiển thị trạng thái kết nối hiện tại và các chế độ truyền.
        """status: Hiển thị trạng thái kết nối hiện tại và các chế độ truyền.
        Sử dụng: status
        """
        if self.connected:
            print("Connection status: Connected.")
            print(f"Host: {self.ftp.host}, Port: {self.ftp.port}")
            print(f"Current local directory: {self.current_local_dir}")
            try:
                print(f"Current FTP directory: {self.ftp.pwd()}")
            except all_errors:
                print("Unable to retrieve the current FTP directory (possibly due to connection error).")
        else: 
            print("Connection status: Not connected.")
        mode = 'ON' if self.prompt_on_mget_mput else 'OFF'
        print(f"Confirmation mode (prompt) for mget/mput: {mode}")
        print(f"File transfer mode: {self.transfer_mode}")
        print(f"Passive FTP mode: {mode}")

    def do_passive(self, args): # Bật/tắt chế độ passive FTP.
        """passive: Bật/tắt chế độ passive FTP.
        Sử dụng: passive
        """
        self.passive_mode = not self.passive_mode
        status = "ON" if self.passive_mode else "OFF"
        print(f"Passive FTP mode: {status}.")
        if self.connected:
            self._ftp_cmd(self.ftp.set_pasv, self.passive_mode)
    
    def do_help(self, args): # Hiển thị danh sách lệnh và hướng dẫn sử dụng.
        """help: Hiển thị danh sách lệnh và hướng dẫn sử dụng.
        Sử dụng: help [lệnh]
        """
        super().do_help(args)

    def do_open(self, args): # Kết nối tới một FTP server bằng hostname/IP và port.
        """open: Kết nối tới một FTP server.
        Sử dụng: open [host] [port]
        Mặc định: host=test.rebex.net, port=21
        """
        if self.connected:
            print(f"Connected to {self.ftp.host}. Please use \'close\' first.")
            return 

        host = Config.FTP_HOST
        port = Config.FTP_PORT

        args = args.split()
        if len(args) > 0: 
            host = args[0]
        if len(args) > 1:
            try:
                port = int(args[1])
            except ValueError:
                print(f"Error: Port is not integer")
                return
            
        print(f"Connecting {host}:{port}...")
        try: 
            self.ftp = FTP()
            self.ftp.connect(host, port, timeout=60)

            # Nhập username and pasword
            user = input(f"User ({host}): ")
            password = input(f"Password: ")

            login_resp = self.ftp.login(user, password)
            print(login_resp)
            self.connected = True
            self.ftp_helpers = FTPHelpers(self.ftp)
            self.current_ftp_dir = self.ftp.pwd()
            print(f"Successfully connected to {host}. Logged in with user: {user}")
            self.ftp.set_pasv(self.passive_mode)
        except all_errors as e:
            print(f"Error connected with FTP: {e}")
            Utils.log_event(f"Error connected to {host}:{port}: {e}", level=logging.ERROR)
            self.ftp = None
            self.connected = False
        except socket.error as e:
            print(f"Network error occurred during connection: {e}")
            Utils.log_event(f"Network error occurred during connection to {host}:{port}: {e}", level=logging.ERROR)
            self.ftp = None
            self.connected = False

    def do_close(self, args): # Ngắt kết nối với FTP server.
        """close: Ngắt kết nối với FTP server.
        Sử dụng: close
        """
        if not self.connected: 
            print("Not connected.")
            return
        resp = self._ftp_cmd(self.ftp.quit)
        if resp: 
            print(resp)
        self.ftp = None
        self.connected = False
        self.ftp_helpers = None
        self.current_ftp_dir = "/"
        print("Disconnected.")
        Utils.log_event("Disconnected to FTP")

    def do_quit(self, args): # Thoát khỏi chương trình client.
        """quit: Thoát khỏi chương trình client.
        Sử dụng: quit
        """
        print(f"Exiting FTP Client.")
        Utils.log_event("Exiting FTP Client.")
        if self.connected: 
            self.do_close("")
        return True

    def do_lcd(self, args): # Thay đổi thư mục làm việc hiện tại của máy cục bộ.
        """lcd: Thay đổi thư mục làm việc hiện tại của máy cục bộ.
        Sử dụng: lcd [đường_dẫn]
        Nếu không có đối số, in ra thư mục hiện tại.
        """
        if not args:
            print(f"Local directory: {self.current_local_dir}")
            return 
        try:
            os.chdir(args)
            self.current_local_dir = os.getcwd()
            print(f"Moved to local directory: {self.current_local_dir}")
            Utils.log_event(f"Moved to local directory: {self.current_local_dir}")
        except OSError as e:
            print(f"Error: Unable to change local directory: {e}")
            Utils.log_event(f"Error: Unable to change local directory: {e}", level=logging.ERROR)
    
    def _recursive_upload(self, local_path, remote_path): # Hàm hỗ trợ tải lên thư mục đệ quy
        try:
            self._ftp_cmd(self.ftp.mkd, remote_path)
        except all_errors as e:
            if "File exists" not in str(e):
                print(f"Error when creating the remote directory {remote_path}: {e}")
                Utils.log_event(f"Error when creating the remote directory {remote_path}: {e}", level=logging.ERROR)
                return
        original_ftp_dir = self.ftp.pwd()
        self._ftp_cmd(self.ftp.cwd, remote_path)

        print("Scanning and uploading files…")
        for item in os.listdir(local_path):
            local_item_path = os.path.join(local_path, item)
            remote_item_path = item

            if os.path.isfile(local_item_path):
                is_clean, message = self.virus_scanner.scan_file(local_item_path)
                if is_clean:
                    if self.ftp_helpers._upload_file(local_item_path, remote_item_path, self.transfer_mode):
                        print(f"  Successfully uploaded {item}")
                    else: 
                        print(f"  Unable to upload {item}")
                else:
                    print(f"  Warning: File {item} - {message}. Will not upload.")  
                    Utils.log_event(f"File {item} not uploaded due to virus: {message}", level=logging.WARNING)
            elif os.path.isdir(local_item_path):
                print(f"  Processing subdirectory: {local_item_path}")
                self._recursive_upload(local_item_path, remote_item_path)

        self._ftp_cmd(self.ftp.cwd, original_ftp_dir) # quay đầu lại thư mục ban đầu

    def do_putdir(self, args):  # Tải lên toàn bộ một thư mục và các thư mục con lên FTP server (recursive upload).
        """putdir: Tải lên toàn bộ một thư mục và các thư mục con lên FTP server (recursive upload).
        Sử dụng: putdir <đường_dẫn_thư_mục_cục_bộ> [đường_dẫn_thư_mục_từ_xa]
        """
        if not self.connected: 
            self.not_connected()
            return 
        if not args:
            print(f"Please provide the local directory path.")
            return 
        
        args = args.split()
        local_dir = args[0]
        remote_dir = args[1] if len(args) > 1 else os.path.basename(local_dir)

        if not os.path.isdir(local_dir):
            print(f"Error: Local directory \'{local_dir}\' does not exist or is not a directory.")

        print(f"Uploading directory {local_dir} to {remote_dir}...")
        self._recursive_upload(local_dir, remote_dir)
        print(f"Upload of directory {local_dir} completed.")
    
    def _recursive_download(self, remote_path, local_path): # Hàm hỗ trợ tải xuống thư mục đệ quy
        os.makedirs(local_path, exist_ok=True)
        original_ftp_dir = self.ftp.pwd()

        try:
            self._ftp_cmd(self.ftp.cwd, remote_path)
        except all_errors as e:
            print(f"Error: Unable to access remote directory {remote_path}: {e}")
            Utils.log_event(f"Error: Unable to access remote directory {remote_path}: {e}", level=logging.ERROR)

        items = []
        self._ftp_cmd(self.ftp.dir, items.append) 

        for line in items:
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
                print(f"  Processing subdirectory: {remote_item_path}")
                self._recursive_download(remote_item_path, local_item_path)
            else: 
                print(f"  Downloading file: {remote_item_path}")
                if self.ftp_helpers._download_file(remote_item_path, local_item_path, self.transfer_mode):
                    print(f"  Successfully downloaded {item_name}")  
                else:  
                    print(f"  Unable to download {item_name}")
        
        self._ftp_cmd(self.ftp.cwd, original_ftp_dir) # Quay lại thư mục ban đầu

    def do_getdir(self, args): # Tải về toàn bộ một thư mục và các thư mục con từ FTP server (recursive download).
        """getdir: Tải về toàn bộ một thư mục và các thư mục con từ FTP server (recursive download).
        Sử dụng: getdir <đường_dẫn_thư_mục_từ_xa> [đường_dẫn_thư_mục_cục_bộ]
        """
        if not self.connected:
            self.not_connected()
            return 
        if not args: 
            print("Please provide the remote directory path.")
            return 
        
        args = args.split()
        remote_dir = args[0]
        local_dir = args[1] if len(args) > 1 else os.path.basename(remote_dir)

        print(f"Downloading directory {remote_dir} to {local_dir}...")  
        self._recursive_download(remote_dir, local_dir)  
        print(f"Download of directory {remote_dir} completed.")
