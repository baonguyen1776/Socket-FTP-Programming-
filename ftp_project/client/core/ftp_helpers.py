from .raw_socket_ftp import FTP 
import os
from .utils import Utils
from .config import Config
import logging

class FTPHelpers:
    def __init__(self, ftp_connection, root=None):
        self.ftp = ftp_connection
        self.root = root

    def _download_file(self, remote_path, local_path, transfer_mode, progress_callback=None):
        Utils.log_event(f"Downloading {remote_path} to {local_path} ({transfer_mode})...")
        try:
            if transfer_mode == 'binary':
                total_size = self.ftp.size(remote_path)
                transferred = [0]

                def handle_block(block):
                    with open(local_path, "ab") as f:
                        f.write(block)
                    transferred[0] += len(block)
                    if progress_callback:
                        if self.root:
                            self.root.after(0, lambda: progress_callback(transferred[0], total_size))
                        else:
                            progress_callback(transferred[0], total_size)
                # Mở file ở chế độ ghi mới trước
                open(local_path, "wb").close()
                self.ftp.retrbinary(f"RETR {remote_path}", handle_block, blocksize=8192)
            else:
                with open(local_path, "w", encoding="utf-8") as f:
                    lines = []

                    def handle_line(line):
                        lines.append(line)
                        f.write(line + "\n")
                        if progress_callback:
                            progress_callback(len(lines), None)  # optional for ascii

                    self.ftp.retrlines(f"RETR {remote_path}", handle_line)

            Utils.log_event(f"Successfully downloaded {remote_path} to {local_path}")
            return True

        except Exception as e:
            Utils.log_event(f"Error while downloading file {remote_path}: {e}", level=logging.ERROR)

            if os.path.exists(local_path):
                try:
                    os.remove(local_path)
                    Utils.log_event(f"Removed incomplete local file at {local_path}", level=logging.WARNING)
                except OSError as ose:
                    Utils.log_event(f"Failed to delete incomplete local file {local_path}: {ose}", level=logging.ERROR)

            return False

        
    def _upload_file(self, local_path, remote_path, transfer_mode, progress_callback=None):
        Utils.log_event(f"Uploading {local_path} to {remote_path} ({transfer_mode})...")
        try:
            total_size = os.path.getsize(local_path)
            transferred = [0]

            def handle_block(block):
                transferred[0] += len(block)
                if progress_callback:
                    if self.root:
                        self.root.after(0, lambda: progress_callback(transferred[0], total_size))
                    else:
                        progress_callback(transferred[0], total_size)
                return block
            if transfer_mode == 'binary':
                with open(local_path, "rb") as f:
                    class FileWithCallback:
                        def __init__(self, file_obj, callback):
                            self.file_obj = file_obj
                            self.callback = callback

                        def read(self, blocksize):
                            block = self.file_obj.read(blocksize)
                            if block:
                                self.callback(block)
                            return block

                    wrapped_file = FileWithCallback(f, handle_block)
                    self.ftp.storbinary(f"STOR {remote_path}", wrapped_file, blocksize=8192)
            else:
                with open(local_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    total_lines = len(lines)

                    def line_iter():
                        for i, line in enumerate(lines, 1):
                            if progress_callback:
                                progress_callback(i, total_lines)
                            yield line.rstrip('\n')

                    self.ftp.storlines(f"STOR {remote_path}", line_iter())

            Utils.log_event(f"Successfully uploaded {local_path} to {remote_path}")
            return True

        except Exception as e:
            Utils.log_event(f"Error while uploading file {local_path}: {e}", level=logging.ERROR)
            return False

        