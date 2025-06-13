import os
import subprocess
import logging

class ClamAVScanner: 
    """Class chịu trách nhiệm scan files"""
    def scan_file(self, file_path): 
        try:
            if not os.path.exists(file_path):
                logging.error(f"File not exist: {file_path}")
                return "ERROR_FILE_NOT_FOUND"
            
            command = ["clamscan", "--no-summary", file_path]
            logging.info(f"Executing command: {" ".join(command)}")

            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                logging.info(f"File {file_path} is scanned. Result OK")
                return "OK"
            elif process.returncode == 1: 
                logging.warning(f"File {file_path} is indected with a virus. Output: {stdout.decode().strip()}")
                return "INFECTED"
            else: 
                error_msg = stderr.decode().strip()
                logging.info(f"Error while scanning file {file_path}: {error_msg} ")
                return f"SCAN_ERROR: {error_msg}"
        except FileNotFoundError: 
            logging.error("Command `clamscan` not found. Please ensure ClamAV is installed and included in PATH.")
            return "CLAMAV_NOT_FOUND"
        except Exception as e:
            logging.error(f"Unknown error: {e}")
            return f"UNKNOWN_SCAN_ERROR: {str(e)}"