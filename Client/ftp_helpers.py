from ftplib import FTP 
import os
from .utils import Utils
from .config import Config
import logging

class FTPHelpers:
    def __init__(self, ftp_connection):
        self.ftp = ftp_connection

    def _download_file(self, remote_path, local_path, transfer_mode):
        Utils.log_event(f"Downloading {remote_path} to {local_path} ({transfer_mode})...")
        try:
            if transfer_mode == 'binary':
                with open(local_path, "wb") as f:
                    self.ftp.retrbinary(f"RETR {remote_path}", f.write)
            else:
                with open(local_path, "w", encoding="utf-8") as f:
                    self.ftp.retrlines(f"RETR {remote_path}", f.write)
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
        
    def _upload_file(self, local_path, remote_path, transfer_mode):
        Utils.log_event(f"Uploading {local_path} to {remote_path}({transfer_mode})...")
        try: 
            if transfer_mode == 'binary':
                with open(local_path, "rb") as f:
                    self.ftp.storbinary(f"STOR {remote_path}", f)
            else:
                with open(local_path, "r", encoding="utf-8") as f:
                    self.ftp.storlines(f"STOR {remote_path}", f)
            Utils.log_event(f"Successfully uploaded {local_path} to {remote_path}")
            return True
        except Exception as e:
            Utils.log_event(f"Error upload file {local_path}: {e}", level=logging.ERROR)
            return False
        
