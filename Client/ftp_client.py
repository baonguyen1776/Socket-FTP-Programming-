import socket
import ftplib
import os 
import sys
import struct 
import glob
import shlex 
import readline
import logging

CLAMAV_AGENT_HOST = '127.0.0.1'
CLAMAV_AGENT_PORT = 65432
AGENT_BUFFER_SIZE = 4096
DEFAULT_TRANSFER_MODE = 'binary'

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s', 
                    handlers=[logging.StreamHandler(sys.stdout)])

class FTPClient:
    def __init__(self): 
        self.ftp = None
        self.connected = False
        self.passive_mode = True 
        self.transfer_mode = DEFAULT_TRANSFER_MODE
        self.prompting = True
        self.current_remote_dir = "/"
        self.current_local_dir = os.getcwd()
        self.agent_host = CLAMAV_AGENT_HOST
        self.agent_port = CLAMAV_AGENT_PORT

    def connect_to_agent(self, local_filepath):
        if not os.path.exists(local_filepath):
            logging.error(f"File {local_filepath} does not exist.")
            return "Error_file_not_found"
        if not os.path.isfile(local_filepath):
            logging.error(f"{local_filepath} is not a file.")
            return "Error_not_a_file"
        
        filename = os.path.basename(local_filepath)
        filesize = os.path.getsize(local_filepath)
        logging.info(f"Connecting to ClamAV agent at {self.agent_host}:{self.agent_port} for scanning \'{filename}\' ...")

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                socket.timeout(60) # Set a timeout of 60 seconds
            sock.connect((self.agent_host, self.agent_port))   

            # 1. Send the filename and filesize
            filename_bytes = filename.encode('utf-8')
            sock.sendall(struct.pack('!I', len(filename_bytes)))

            # 2. Send the filename (đẩy toàn bộ tệp tin lên dưới dạng bytes).
            sock.sendall(filename_bytes)

            # 3. Send the file size 
            sock.sendall(struct.pack('!Q', filesize))

            # 4. Send the file content
            bytes_sent = 0
            with open(local_filepath, 'rb') as file:
                while True: 
                    chunk = file.read(AGENT_BUFFER_SIZE)
                    if not chunk:
                        break
                    sock.sendall(chunk)
                    bytes_sent += len(chunk)
            logging.info(f"Sent {bytes_sent} bytes of file {filename} to ClamAV agent.")

            # 5. Receive the scan result
            result_bytes = sock.recv(16)
            scan_result = result_bytes.decode('utf-8').strip()
            logging.info(f"Received scan result: {scan_result}")
            return scan_result

        except socket.timeout:
            logging.error("Connection to ClamAV agent timed out.")
            return "Error_connection_timeout"
        except socket.error as e:
            logging.error(f"Socket error connecting to ClamAV agent: {e}")
            return "Error_socket_error"
        except struct.error as e: # Lỗi khi đóng gói hoặc giải nén dữ liệu
            logging.error(f"Struct packing/unpacking error: {e}")
            return "Error_struct_error"
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            return "Error_unexpected_error"
    

    def _ftp_cmd(self, func, *args, **kwargs):
        if not self.connected:
            print("Error: Not connected to any server. Use 'open <host>'.")
            return None
        try:
            # Đảm bảo rằng các lệnh FTP được thực thi trong chế độ thụ động nếu cần thiết
            is_data_transfer = func.__name__ in (
                'nlst', 'retrbinary', 'retrlines', 'storbinary', 'storlines', 'dir'
            )

            if is_data_transfer:
                 self.ftp.set_pasv(self.passive_mode)
                 logging.debug(f"Set passive mode to {self.passive_mode} for {func.__name__}")

            return func(*args, **kwargs)
        except ftplib.error_perm as e:
            print(f"FTP permission error: {e}")
        except ftplib.error_temp as e:
            print(f"FTP temporary error: {e}")
        except ftplib.error_proto as e:
            print(f"FTP protocol error: {e}")
        except ftplib.all_errors as e:
            print(f"FTP error: {e}")
        except socket.gaierror as e:
            print(f"Network error (address lookup): {e}")
            self.connected = False
            self.ftp = None
        except socket.error as e:
            print(f"Network error (socket): {e}")
            self.connected = False
            self.ftp = None
        return None

    # Directory Operations
    def do_ls(self, args):
        path = args[0] if args else "."
        print(f"Listing directory: {path}")
        self._ftp_cmd(self.ftp.dir, path)

    def do_cd(self, args): 
        if not args:
            print("Usage: cd <remote_directory>")
            return
        path = args[0]
        resp = self._ftp_cmd(self.ftp.cwd, path)
        if resp: 
            self.current.remote_dir = self._ftp_cmd(self.ftp.pwd)
            print(f"Changed directory to: {self.current_remote_dir}")

    def do_lcd(self, args):
        if not args:
            print(f"Current local directory: {self.current_local_dir}")
            return
        path = args[0]
        try:
            os.chdir(path)
            self.current_local_dir = os.getcwd()
            print(f"Local directory changed to : {self.current_local_dir}")
        except FileNotFoundError:
            print(f"Error: local directory not found: {path}")
        except Exception as e:
            print(f"Error changing local directory: {e}")

    def do_pwd(self, args):
        remote_dir = self._ftp_cmd(self.ftp.pwd)
        if remote_dir:
            self.current_remote_dir= remote_dir
            print(f"Current remote directory: {self.current_remote_dir}")

    def do_mkdir(self, args):
        if not args:
            print("Usage: mkdir <directory_name>")
            return
        path = args[0]
        resp = self._ftp_cmd(self.ftp.mkd, path)
        if resp:
            print(f"Directory created: {path}")

    def do_rmdir(self, args):
        if not args:
            print("Usage: rmdir <directory_name>")
            return
        path = args[0]
        resp = self._ftp_cmd(self.ftp.rmd, path)
        if resp:
            print(f"Directory removed: {path}")

    def do_delete(self, args):
        if not args:
            print("Usage: delete <remote_filename>")
            return
        path = args[0]
        resp = self._ftp_cmd(self.ftp.delete, path)
        if resp:
            print(f"File deleted: {path}")

    def do_rename(self, args):
        if len(args) != 2:
            print("Usage: rename <from_name> <to_name>")
            return
        from_name, to_name = args
        resp = self._ftp_cmd(self.ftp.rename, from_name, to_name)
        if resp:
            print(f"File renamed: {resp}")

    # Session Management
    def do_open(self, args): 
        if self.connected:
            print("")
            print(f"Already connected to {self.ftp.host}. Use 'close' to disconnect first.")
            return 
        if not args:
            print("Usage: open <host> [port])")
            return 

        host = args[0]
        port = 21
        if len(args) > 1:
            try: 
                port = int(args[1])
            except ValueError:
                print(f"Invalid port number: {args[1]}. Using default port 21.")
                return
            
            # try: 
            #     self.ftp = ftplib.FTP()
            #     self.ftp.connect(host, port)
            # ....
            # except....

    def do_close(self, args): 
        if not self.connected:
            print("Not connected")
            return
        resp = self._ftp_cmd(self.ftp.quit)
        if resp:
            print(resp)
        self.ftp = None
        self.connected = False
        self.current_remote_dir = "/"
        print("Connection closed.")

    def do_quit(self, args):
        if self.connected:
            self.do_close([])
        print("Goodbye!")
        sys.exit(0)
    
