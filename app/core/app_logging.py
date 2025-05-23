import logging
from logging.handlers import RotatingFileHandler
import os
from app.core.config import settings 

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO) 

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if not settings.TESTING:
        try:
            
            log_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "logs")
            os.makedirs(log_directory, exist_ok=True) 
            log_file_path = os.path.join(log_directory, 'app.log')

            file_handler = RotatingFileHandler(log_file_path, maxBytes=10000000, backupCount=5)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.error(f"Failed to set up file logging: {e}", exc_info=True)