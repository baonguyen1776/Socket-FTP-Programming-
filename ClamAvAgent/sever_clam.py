import socket
import logging
import os
from handler import ClientHandler
from scanner import ClamAVScanner

TEMP_DIR = 'temp_scan_files'

class ClamAVAgentServer:
    """Lớp server chính của ClamAV Agent, lắng nghe kết nối và tạo handler cho mỗi client."""
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sever_socket = None
        self.scanner = ClamAVScanner()

        if not os.path.exists(TEMP_DIR):
            try:
                os.makedirs(TEMP_DIR)
                logging.info(f"Temporary directory {TEMP_DIR} has been created")
            except OSError as e: 
                logging.error(f"Error: Unable to create temporary directory {TEMP_DIR}: {e}")

    def start(self):
        try: 
            self.sever_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sever_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sever_socket.bind((self.host, self.port))
            self.sever_socket.listen(3) 
            logging.info(f"ClamAV Agent is listening on {self.host}:{self.port}")

            while True:
                try:
                    client_socket, client_address = self.sever_socket.accept()
                    client_socket.timeout(60)
                    handler = ClientHandler(client_socket, client_address, self.scanner)
                    handler.start()
                except socket.timeout():
                    logging.warning("Server socket accept timed out. Continuing to listen...")
                    continue
                except OSError as e: 
                    logging.error(f"Error OS to connected: {e}")
                    break
                except Exception as e:
                    logging.error(f"Unknown error accepting connection: {e}")
        except socket.error as e:
            logging.error(f"Error socket creat server: {e}")
        except Exception as e:
            logging.error(f"Unknown error: {e}")
        finally:
            self._stop()

    def _stop(self): 
        logging.info("Stopping ClamAV Agent Server...")
        if self.sever_socket:
            try: 
                self.sever_socket.close()
                logging.info("Close!")
            except Exception as e:
                logging.info("Error: {e}")
        if os.path.exists(TEMP_DIR):
            try:
                import shutil
                shutil.rmtree(TEMP_DIR)
                logging.info(f"Temporary directory {TEMP_DIR} has been deleted.")
            except OSError as e:
                logging.error("Error: Unable to delete temporary directory {TEMP_DIR} when stopping server: {e}")
