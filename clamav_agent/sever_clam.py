import socket
import logging
import os 
import signal
from typing import Tuple
from handler import ClientHandler
from scanner import ClamAVScanner

TEMP_DIR = 'temp_scan_files'

class ClamAVAgentServer:
    """Lớp server chính của ClamAV Agent, lắng nghe kết nối và tạo handler cho mỗi client."""
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.server_socket: socket.socket | None = None
        self.scanner = ClamAVScanner()
        self.running = False

        if not os.path.exists(TEMP_DIR):
            try:
                os.makedirs(TEMP_DIR)
                logging.info(f"Created temporary directory: {TEMP_DIR}")
            except OSError as e:
                logging.error(f"Unable to create temporary directory {TEMP_DIR}: {e}")

    def signal_handler(self, signum, frame):
        """Signal handler for graceful shutdown"""
        logging.info(f"Received signal {signum}. Initiating graceful shutdown...")
        self.running = False
        if self.server_socket:
            self.server_socket.close()

    def start(self):
        # Đăng ký signal handlers cho graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)    # Ctrl+C
        signal.signal(signal.SIGTERM, self.signal_handler)   # Terminate signal
        
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Đặt timeout cho server socket để không block vô hạn
            self.server_socket.settimeout(1.0)  # Timeout 1 giây
            
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(3)
            self.running = True
            
            logging.info(f"ClamAV Agent is listening on {self.host}:{self.port}")
            logging.info("Press Ctrl+C to stop the server gracefully...")

            while self.running: 
                try:
                    client_socket: socket.socket
                    client_address = Tuple[str, int]
                    client_socket, client_address = self.server_socket.accept()

                    client_socket.settimeout(60)
                    handler = ClientHandler(client_socket, client_address, self.scanner)
                    handler.start()
                except socket.timeout:
                    # Timeout bình thường, kiểm tra self.running và tiếp tục
                    continue
                except OSError as e:
                    if self.running:  # Chỉ log error nếu server vẫn đang chạy
                        logging.error(f"OS error while accepting connection: {e}")
                    break  # Thoát khỏi loop nếu socket bị đóng
                except Exception as e:
                    if self.running:
                        logging.error(f"Unknown error while accepting connection: {e}")

        except socket.error as e:
            logging.error(f"Socket error while initializing server: {e}")
        except Exception as e:
            logging.error(f"Unexpected error in server: {e}")
        finally:
            self.stop()
    
    def stop(self):
        logging.info("Stopping ClamAV Agent Server...")
        self.running = False
        
        if self.server_socket:
            try:
                self.server_socket.close()
                logging.info("Server socket closed successfully")
            except Exception as e:
                logging.error(f"Error closing ClamAV Server socket: {e}")
        
        if os.path.exists(TEMP_DIR):
            try:
                import shutil
                shutil.rmtree(TEMP_DIR)
                logging.info(f"Temporary directory {TEMP_DIR} deleted successfully")
            except OSError as e:
                logging.error(f"Cannot delete temporary directory {TEMP_DIR}: {e}")
        
        logging.info("ClamAV Agent Server stopped gracefully")