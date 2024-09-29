import logging
from logging.handlers import RotatingFileHandler

def setup_logger(name='my_logger', log_file='app.log', level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        handler = RotatingFileHandler(log_file, maxBytes=10000000, backupCount=5)
        handler.setLevel(level)
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
    
    return logger
