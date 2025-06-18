import socket
import threading
import os
import logging
from typing import Tuple
from scanner import ClamAVScanner

BUFFER_SIZE = 4096
TEMP_DIR = 'temp_scan_file'

class ClientHandler(threading.Thread):
    """Lớp xử lý kết nối từ mỗi client."""

    def __init__(self, client_socket: socket.socket, client_address: Tuple[str, int], scanner: ClamAVScanner):
        super().__init__()
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.clien_address = client_address
        self.scanner = scanner
        logging.info(f"New connect from {self.clien_address}")
    
    def run(self):
        try: 
            # 1. nhận tên file từ client
            file_name_files = self.client_socket.recv(BUFFER_SIZE)
            if not file_name_files:
                logging.warning(f"The client {self.client_address} disconnected before sending the file name.")
                return
            
            file_name = file_name_files.decode().strip()
            logging.info(f"Client {self.clien_address} want to scan {file_name}")

            if not os.path.exists(TEMP_DIR): 
                os.makedirs(TEMP_DIR)
            
            # Đường dẫn lưu file tạm
            # Tránh các vấn đề về path traversal bằng cách chỉ lấy basename
            safe_file_name = os.path.basename(file_name)
            temp_file_path = os.path.join(TEMP_DIR, safe_file_name)

            # 2. Nhận nội dung file từ client và lưu vào file tạm
            self.client_socket.sendall(b"READY")
            logging.info(f"File {safe_file_name} is being received from {self.client_address}")
            with open(temp_file_path, 'wb') as f:
                while True:
                    chunk = self.client_socket.recv(BUFFER_SIZE)
                    if not chunk:
                        break
                    f.write(chunk)
            logging.info(f"File {safe_file_name} has been successfully received from {self.client_address} and saved at {temp_file_path}")

            # 3. Bắt đầu quét file:
            scan_result: str = self.scanner.scan_file(temp_file_path)
            logging.info(f"Scan result for {safe_file_name}: {scan_result}")

            # 4. Gửi kết quả quét lại cho client
            self.client_socket.sendall(scan_result.encode())
            logging.info(f"The result '{scan_result}' has been sent to {self.client_address}")
        except ConnectionResetError: 
            logging.warning(f"Client {self.client_address} has unexpectedly closed the connection") 
        except socket.timeout:
            logging.warning(f"Timeout occurred from client {self.client_address}")
        except Exception as e:
            logging.error(f"Error occurred while processing client {self.client_address}: {e}")
            try: 
                self.client_socket.sendall(f"AGENT_ERROR: {str(e)}".encode())
            except Exception as e:
                logging.error(f"Unable to send error notification to client {self.client_address}: {e}")
        finally: 
            # Clear file tạm để bảo mật trước khi out
            if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                    logging.info(f"Temporary file deleted: {temp_file_path}")
                except OSError as e:
                    logging.error(f"Unable to delete temporary file {temp_file_path}: {e}")
            self.client_socket.close()
            logging.info(f"Connection closed with {self.client_address}")