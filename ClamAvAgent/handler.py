import socket
import threading
import os
import logging
import struct 
from typing import Tuple
from scanner import ClamAVScanner

BUFFER_SIZE = 4096
TEMP_DIR = 'temp_scan_file'

class ClientHandler(threading.Thread):
    """Lớp xử lý kết nối từ mỗi client."""

    def __init__(self, client_socket: socket.socket, client_address: Tuple[str, int], scanner: ClamAVScanner):
        super().__init__()
        self.client_socket = client_socket
        self.client_address = client_address
        self.scanner = scanner
        logging.info(f"New connect from {self.client_address}")
    
    def run(self):
        temp_file_path = None # Initialize to None for finally block
        try: 
            # 1. Nhận độ dài tên file (4 bytes)
            filename_len_bytes = self.client_socket.recv(4)
            if not filename_len_bytes:
                logging.warning(f"Client {self.client_address} disconnected before sending filename length.")
                return
            filename_len = struct.unpack("!I", filename_len_bytes)[0]

            # 2. Nhận tên file
            filename_bytes = self.client_socket.recv(filename_len)
            if not filename_bytes:
                logging.warning(f"Client {self.client_address} disconnected before sending filename.")
                return
            file_name = filename_bytes.decode("utf-8").strip()
            logging.info(f"Client {self.client_address} wants to scan file: {file_name}")

            # 3. Nhận kích thước file (8 bytes)
            filesize_bytes = self.client_socket.recv(8)
            if not filesize_bytes:
                logging.warning(f"Client {self.client_address} disconnected before sending file size.")
                return
            filesize = struct.unpack("!Q", filesize_bytes)[0]
            logging.info(f"File {file_name} size: {filesize} bytes.")

            if not os.path.exists(TEMP_DIR): 
                os.makedirs(TEMP_DIR)
            
            # Đường dẫn lưu file tạm
            safe_file_name = os.path.basename(file_name)
            temp_file_path = os.path.join(TEMP_DIR, safe_file_name)

            # 4. Nhận nội dung file từ client và lưu vào file tạm
            logging.info(f"Receiving file {safe_file_name} from {self.client_address}")
            bytes_received = 0
            with open(temp_file_path, 'wb') as f:
                while bytes_received < filesize:
                    chunk = self.client_socket.recv(min(BUFFER_SIZE, filesize - bytes_received))
                    if not chunk:
                        logging.warning(f"Client {self.client_address} disconnected prematurely while sending file {safe_file_name}.")
                        break
                    f.write(chunk)
                    bytes_received += len(chunk)
            logging.info(f"Received {bytes_received} bytes for file {safe_file_name} from {self.client_address}, saved at {temp_file_path}")

            # 5. Quét file
            scan_result: str = self.scanner.scan_file(temp_file_path)
            logging.info(f"Scan result for {safe_file_name}: {scan_result}")

            # 6. Gửi kết quả quét lại cho client
            # Client mong đợi 16 bytes, nên đảm bảo kết quả đủ 16 bytes
            result_to_send = scan_result.ljust(16).encode("utf-8")[:16] # Pad or truncate to 16 bytes
            self.client_socket.sendall(result_to_send)
            logging.info(f"Sent result '{scan_result}' to {self.client_address}")

        except ConnectionResetError: 
            logging.warning(f"Client {self.client_address} has unexpectedly closed the connection") 
        except socket.timeout:
            logging.warning(f"Timeout occurred from client {self.client_address}")
        except struct.error as e:
            logging.error(f"Protocol error (struct unpacking) with client {self.client_address}: {e}")
        except Exception as e:
            logging.error(f"Error occurred while processing client {self.client_address}: {e}")
            try: 
                # Attempt to send an error message back to the client
                error_msg = f"AGENT_ERROR: {str(e)}"
                self.client_socket.sendall(error_msg.ljust(16).encode("utf-8")[:16])
            except Exception as send_e:
                logging.error(f"Unable to send error notification to client {self.client_address}: {send_e}")
        finally: 
            # Dọn dẹp file tạm
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                    logging.info(f"Temporary file deleted: {temp_file_path}")
                except OSError as e:
                    logging.error(f"Unable to delete temporary file {temp_file_path}: {e}")
            self.client_socket.close()
            logging.info(f"Connection closed with {self.client_address}")