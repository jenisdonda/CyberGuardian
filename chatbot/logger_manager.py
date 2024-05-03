import logging

def initialize_logger(logger_name, log_file_path):
    """
    Initializes a logger with the specified name and log file path.

    Parameters:
    - logger_name (str): The name of the logger.
    - log_file_path (str): The file path to save the log.

    Returns:
    - logger: The initialized logger object or None if an exception occurs.
    """
    try:
        maxbytes = 10 * 1024 * 1024
        backuplogs = 1

        log_level = logging.INFO
        logger = logging.getLogger(logger_name)
        ch = logging.handlers.RotatingFileHandler(log_file_path, maxBytes=maxbytes, backupCount=backuplogs)
        formatter = logging.Formatter("%(asctime)s - %(thread)s -%(name)s - %(levelname)s - %(message)s - %(funcName)-18s")
        ch.setFormatter(formatter)

        logger.addHandler(ch)
        logger.setLevel(log_level)
        return logger
    
    except Exception as ex:
        return None
