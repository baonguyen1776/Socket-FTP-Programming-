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
            






