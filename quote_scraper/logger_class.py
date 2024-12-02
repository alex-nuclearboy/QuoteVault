import os
import logging


class Logger:
    """
    A class to manage loggers for different modules and websites.
    Logs messages to both a file and the console.
    """
    def __init__(self, site_name: str, module_name: str,
                 log_level: int = logging.DEBUG):
        """
        Initialize the Logger instance for a specific site and module.

        :param site_name: The name of the website
        :type site_name: str
        :param module_name: The name of the module (for distinguishing logs)
        :type module_name: str
        :param log_level: The logging level (default is logging.DEBUG)
        :type log_level: int
        """
        self.site_name = site_name
        self.module_name = module_name
        self.log_level = log_level
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """
        Set up and return a logger instance with handlers
        for both file and console output.

        :return: A logger instance with file and console handlers.
        :rtype: logging.Logger
        """
        logger = logging.getLogger(self.module_name)

        # Ensure logs directory exists
        log_dir = os.path.join('logs', self.site_name)
        if not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir)
            except OSError as e:
                raise OSError(f"Error creating log directory '{log_dir}': {e}")

        log_file_path = os.path.join(log_dir, f'{self.module_name}.log')
        try:
            file_handler = logging.FileHandler(log_file_path)
        except OSError as e:
            raise OSError(f"Error opening log file '{log_file_path}': {e}")

        console_handler = logging.StreamHandler()

        file_handler.setLevel(self.log_level)
        console_handler.setLevel(self.log_level)

        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.setLevel(self.log_level)

        return logger

    def get_logger(self) -> logging.Logger:
        """
        Return the logger instance.

        :return: The logger instance.
        :rtype: logging.Logger
        """
        return self.logger
