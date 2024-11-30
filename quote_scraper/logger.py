import os
import logging


def setup_logger(
    name: str, log_file: str, level: int = logging.DEBUG
) -> logging.Logger:
    """
    Set up a logger that outputs log messages both to a file
    and to the console.

    :param name: The name of the logger
    :type name: str
    :param log_file: The name of the log file where logs will be stored
    :type log_file: str
    :param level: The logging level (default is logging.DEBUG). This determines
                  the severity of messages to log (e.g., DEBUG, INFO, ERROR)
    :type level: int

    :return: A logger instance configured with the specified settings
    :rtype: logging.Logger

    :raises OSError: If there is an error creating the logs directory
                     or opening the log file.
    """
    logger = logging.getLogger(name)

    # Ensure logs directory exists
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
        except OSError as e:
            raise OSError(f"Error creating log directory '{log_dir}': {e}")

    log_path = os.path.join(log_dir, log_file)
    try:
        handler = logging.FileHandler(log_path)
    except OSError as e:
        raise OSError(f"Error opening log file '{log_path}': {e}")

    console_handler = logging.StreamHandler()

    handler.setLevel(level)
    console_handler.setLevel(level)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.addHandler(console_handler)
    logger.setLevel(level)

    return logger
