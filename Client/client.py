from ftp_command import FTPCommands
from utils import Utils
import logging

class FTPClientApp(FTPCommands):
    def __init__(self):
        super().__init__()
        Utils.log_event("FTP Client application has started.", level=logging.INFO)

    def start(self):
        self.cmdloop()