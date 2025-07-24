import logging 
from .config import Config

# Cấu hình logging
logging.basicConfig(level=Config.LOG_LEVEL, 
                    format="%(asctime)s - %(levelname)s - %(message)s", 
                    handlers=[
                        logging.StreamHandler(), 
                        logging.FileHandler(Config.LOG_FILE)
                    ])

class Utils: 
    @staticmethod
    def log_event(msg, level=logging.INFO):
        if level == logging.DEBUG:
            logging.debug(msg)
        elif level == logging.INFO:
            logging.info(msg)
        elif level == logging.WARNING:
            logging.warning(msg)
        elif level == logging.ERROR:
            logging.error(msg)
        elif level == logging.CRITICAL:
            logging.critical(msg)
        else: 
            logging.info(msg)