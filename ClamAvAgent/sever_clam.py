import socket
import logging
import os 
from typing import Tuple
from handler import ClientHandler
from scanner import ClamAVScanner

TEMP_DIR = 'temp_scan_files'

class ClamAVAgentServer:
    """Lớp server chính của ClamAV Agent, lắng nghe kết nối và tạo handler cho mỗi client."""
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.sever_socket: socket.socket | None = None
        self.scanner = ClamAVScanner()

        if not os.path.exists(TEMP_DIR):
            try:
                os.makedirs(TEMP_DIR)
                logging.info(f"Created temporary directory: {TEMP_DIR}")
            except OSError as e:
                logging.error(f"Unable to create temporary directory {TEMP_DIR}: {e}")

    def start(self):
        try:
            self.sever_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sever_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sever_socket.bind((self.host, self.port))
            self.sever_socket.listen(3)
            logging.info(f"ClamAV Agent is listening on {self.host}:{self.port}")

            while True: 
                try:
                    client_socket: socket.socket
                    client_address = Tuple[str, int]
                    client_socket, client_address = self.sever_socket.accept()

                    client_socket.timeout(60)
                    handler = ClientHandler(client_socket, client_address, self.scanner)
                    handler.start()
                except socket.timeout:
                    logging.warning("Server socket accept timed out. Continuing to listen...")
                    continue
                except OSError as e:
                    logging.error(f"OS error while accepting connection: {e}")
                except Exception as e:
                    logging.error(f"Unknown error while accepting connection: {e}")

        except socket.error as e:
            logging.error(f"Socket error while initializing server: {e}")
        except Exception as e:
            logging.error(f"Unexpected error in server: {e}")
        finally:
            self.stop()
    
    def stop(self):
        logging.info("Stopping ClamAV Agent Server...")
        if self.sever_socket:
            try:
                self.sever_socket.close()
                logging.info(f"Server socket is closed")
            except Exception as e:
                logging.error(f"Error close ClamAV Server")
        
        if os.path.exists(TEMP_DIR):
            try:
                import shutil
                shutil.rmtree(TEMP_DIR)
                logging.info(f"Delete dir temp: {TEMP_DIR}")
            except OSError as e:
                logging.error(f"Cannot delete directory {TEMP_DIR}")