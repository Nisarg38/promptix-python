import logging
import sys

# ANSI escape codes for colors
YELLOW = "\033[93m"
BLUE = "\033[94m"
GRAY = "\033[90m"
RESET = "\033[0m"

class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to different log levels."""
    
    def format(self, record):
        # Add colors based on log level
        if record.levelno == logging.WARNING:
            # Ensure warning appears on its own line and ends with a newline
            record.msg = f"\n{YELLOW}[WARNING] {record.msg}{RESET}\n"
        elif record.levelno == logging.INFO:
            record.msg = f"{BLUE}[INFO] {record.msg}{RESET}"
        elif record.levelno == logging.DEBUG:
            record.msg = f"{GRAY}[DEBUG] {record.msg}{RESET}"
        return super().format(record)

def setup_logging(level=logging.INFO):
    """Setup logging with a clean, minimal format and colors."""
    # Disable existing loggers to prevent duplicates
    logging.getLogger().handlers = []
    
    logger = logging.getLogger("promptix")
    logger.handlers = []  # Clear any existing handlers
    logger.propagate = False  # Prevent propagation to root logger
    
    # Create handlers for different log levels
    info_handler = logging.StreamHandler(sys.stdout)
    warning_handler = logging.StreamHandler(sys.stderr)
    
    # Set formatters
    formatter = ColoredFormatter('%(message)s')
    info_handler.setFormatter(formatter)
    warning_handler.setFormatter(formatter)
    
    # Set level filters
    info_handler.addFilter(lambda record: record.levelno <= logging.INFO)
    warning_handler.setLevel(logging.WARNING)
    
    # Add handlers
    logger.addHandler(info_handler)
    logger.addHandler(warning_handler)
    logger.setLevel(level)
    
    return logger 