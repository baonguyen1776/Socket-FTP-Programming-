import sys
import os

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from core.ftp_command import FTPCommands
from core.raw_socket_ftp import FTP

if __name__ == "__main__":
    ftp = FTP()
    client = FTPCommands(ftp)
    client.cmdloop()