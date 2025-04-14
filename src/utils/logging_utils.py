import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(name=None):
    """
    Set up a logger with console and file handlers.
    
    Args:
        name: Logger name (defaults to root logger)
        
    Returns:
        Logger instance
    """
    # Get or create logger
    logger = logging.getLogger(name)
    
    # Only configure if it hasn't been configured yet
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Create formatters
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Create log directory if it doesn't exist
        log_dir = os.path.join(os.getcwd(), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # Create file handler
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, 'breweries_pipeline.log'),
            maxBytes=10485760,  # 10 MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger
