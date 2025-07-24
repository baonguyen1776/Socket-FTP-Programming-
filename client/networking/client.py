#!/usr/bin/env python3
"""
Network client entry point
"""

import sys
import os

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from ..core.ftp_command import FTPCommands
from ..core.raw_socket_ftp import FTP
from ..core.utils import Utils
import logging

class FTPClientApp(FTPCommands):
    def __init__(self):
        ftp = FTP()
        super().__init__(ftp)
        Utils.log_event("FTP Client application has started.", level=logging.INFO)

    def start(self):
        self.cmdloop()

if __name__ == "__main__":
    client = FTPClientApp()
    client.start()