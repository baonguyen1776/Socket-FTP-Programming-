import socket
import struct
import os
from .config import Config
from .utils import Utils
import logging

class VirusScan:
    def __init__(self):
        self.agent_host = Config.CLAMAV_AGENT_HOST
        self.agent_port = Config.CLAMAV_AGENT_PORT
        self.buffer_size = Config.CLAMAV_BUFFER_SIZE

    # Gửi file đến ClamAV Agent để quét virus và nhận kết quả.
    def scan_file(self, filepath):
        if not os.path.exists(filepath):
            Utils.log_event(f"Error: Local file not found: {filepath}", level=logging.ERROR)
            return False, "ERROR_FILENOTFOUND"
        if not os.path.isfile(filepath):
            Utils.log_event(f"Error: Not a file: {filepath}", level=logging.ERROR)
            return False, "ERROR_NOTFILE"
        
        filename = os.path.basename(filepath)
        filesize = os.path.getsize(filepath)
        Utils.log_event(f"Connecting to ClamAV Agent at {self.agent_host}:{self.agent_port} to scan \'{filename}\'...")

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(600)
                sock.connect((self.agent_host, self.agent_port))

                # 1. Gửi độ dài tên file (4 bytes, network byte order)
                filename_bytes = filename.encode("utf-8")
                sock.sendall(struct.pack("!I", len(filename_bytes)))

                # 2. Gửi tên file
                sock.sendall(filename_bytes)

                # 3. Gửi kích thước (8 bytes, network byte order)
                sock.sendall(struct.pack("!Q", filesize))

                # 4. Gửi dữ liệu file
                bytes_sent = 0
                with open(filepath, "rb") as f:
                    while True:
                        chunk = f.read(self.buffer_size)
                        if not chunk:
                            break
                        sock.sendall(chunk)
                        bytes_sent += len(chunk)
                Utils.log_event(f"Send {bytes_sent} bytes to agent.", level=logging.DEBUG)

                # 5. Nhận kết quả từ agent
                result_bytes = sock.recv(16)
                scan_result = result_bytes.decode("utf-8").strip()
                Utils.log_event(f"Virus scan result for \'{filename}\': {scan_result}")

                if scan_result == "OK":
                    return True, "Good file."
                else:
                    return False, "Bad file."
        except socket.timeout:
            Utils.log_event(f"Error: Connecting to ClamAV agent has timed out.", level=logging.ERROR)
            return False, "ERROR_TIMEOUT"
        except socket.error as e: 
            Utils.log_event(f"A socket error occurred while connecting to the ClamAV agent: {e}", level=logging.ERROR)
            return False, "ERROR_CONNECTION"
        except struct.error as e:
            Utils.log_event(f"Error in packing/unpacking data structures: {e}", level=logging.ERROR)
            return False, "ERROR_PROTOCOL"
        except Exception as e:
            Utils.log_event(f"An unexpected error occurred while communicating with the agent: {e}", level=logging.ERROR)
            return False, "ERROR_UNKNOWN"


