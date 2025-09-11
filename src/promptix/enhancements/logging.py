"""
Enhanced logging module for Promptix with structured logging capabilities.

This module provides comprehensive logging functionality with support for:
- Structured logging with JSON output
- Configurable log levels
- Multiple output formats (colored console, JSON, plain text)
- Context injection for better traceability
- Performance monitoring capabilities
"""

import json
import logging
import os
import sys
import time
from contextvars import ContextVar
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union
from enum import Enum

# Context variables for structured logging
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar('user_id', default=None)
operation_var: ContextVar[Optional[str]] = ContextVar('operation', default=None)

# ANSI escape codes for colors
class Colors:
    """ANSI color codes for terminal output."""
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

class LogFormat(Enum):
    """Supported log output formats."""
    COLORED = "colored"
    JSON = "json"
    PLAIN = "plain"

class StructuredFormatter(logging.Formatter):
    """
    Advanced formatter that supports structured logging with JSON output.
    
    Features:
    - JSON structured output for production environments
    - Colored console output for development
    - Context injection from ContextVars
    - Performance timing information
    - Error stack traces in structured format
    """
    
    def __init__(self, format_type: LogFormat = LogFormat.COLORED, include_context: bool = True):
        """
        Initialize the structured formatter.
        
        Args:
            format_type: The output format to use
            include_context: Whether to include context variables in logs
        """
        super().__init__()
        self.format_type = format_type
        self.include_context = include_context
        
        # Color mapping for different log levels
        self.color_map = {
            logging.DEBUG: Colors.GRAY,
            logging.INFO: Colors.BLUE,
            logging.WARNING: Colors.YELLOW,
            logging.ERROR: Colors.RED,
            logging.CRITICAL: Colors.RED + Colors.BOLD,
        }
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record according to the specified format type.
        
        Args:
            record: The log record to format
            
        Returns:
            Formatted log message string
        """
        # Create base log data
        log_data = self._create_base_log_data(record)
        
        # Add context information if enabled
        if self.include_context:
            log_data.update(self._get_context_data())
        
        # Add performance information if available
        if hasattr(record, 'duration'):
            log_data['duration_ms'] = record.duration
        
        # Format according to type
        if self.format_type == LogFormat.JSON:
            return self._format_json(log_data)
        elif self.format_type == LogFormat.COLORED:
            return self._format_colored(log_data, record)
        else:  # PLAIN
            return self._format_plain(log_data)
    
    def _create_base_log_data(self, record: logging.LogRecord) -> Dict[str, Any]:
        """Create the base log data structure."""
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception information if present
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': self.formatException(record.exc_info)
            }
        
        # Add extra fields from the log record
        extra_fields = {k: v for k, v in record.__dict__.items() 
                       if k not in logging.LogRecord(
                           'dummy', 0, 'dummy', 0, 'dummy', (), None
                       ).__dict__}
        if extra_fields:
            log_data['extra'] = extra_fields
        
        return log_data
    
    def _get_context_data(self) -> Dict[str, Any]:
        """Get context data from ContextVars."""
        context = {}
        
        if request_id := request_id_var.get():
            context['request_id'] = request_id
        if user_id := user_id_var.get():
            context['user_id'] = user_id
        if operation := operation_var.get():
            context['operation'] = operation
            
        return context
    
    def _format_json(self, log_data: Dict[str, Any]) -> str:
        """Format log data as JSON."""
        return json.dumps(log_data, default=str)
    
    def _format_colored(self, log_data: Dict[str, Any], record: logging.LogRecord) -> str:
        """Format log data with colors for console output."""
        color = self.color_map.get(record.levelno, Colors.WHITE)
        timestamp = log_data['timestamp']
        level = log_data['level']
        message = log_data['message']
        
        # Build context string
        context_parts = []
        if 'request_id' in log_data:
            context_parts.append(f"req_id={log_data['request_id']}")
        if 'operation' in log_data:
            context_parts.append(f"op={log_data['operation']}")
        if 'duration_ms' in log_data:
            context_parts.append(f"duration={log_data['duration_ms']:.2f}ms")
        
        context_str = f" [{', '.join(context_parts)}]" if context_parts else ""
        
        return f"{color}[{timestamp}] {level:8s}{Colors.RESET} {message}{context_str}"
    
    def _format_plain(self, log_data: Dict[str, Any]) -> str:
        """Format log data as plain text."""
        timestamp = log_data['timestamp']
        level = log_data['level']
        message = log_data['message']
        
        return f"[{timestamp}] {level:8s} {message}"

class PerformanceLogger:
    """
    Context manager for performance logging.
    
    Usage:
        with PerformanceLogger("database_query", logger):
            # Your code here
            pass
    """
    
    def __init__(self, operation: str, logger: logging.Logger, level: int = logging.INFO):
        """
        Initialize performance logger.
        
        Args:
            operation: Name of the operation being timed
            logger: Logger instance to use
            level: Log level for the performance message
        """
        self.operation = operation
        self.logger = logger
        self.level = level
        self.start_time: Optional[float] = None
    
    def __enter__(self):
        """Start timing the operation."""
        self.start_time = time.perf_counter()
        operation_var.set(self.operation)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End timing and log the duration."""
        if self.start_time is not None:
            duration = (time.perf_counter() - self.start_time) * 1000  # Convert to milliseconds
            self.logger.log(
                self.level,
                f"Operation '{self.operation}' completed",
                extra={'duration': duration}
            )

def setup_logging(
    level: Union[int, str] = logging.INFO,
    format_type: Union[LogFormat, str] = LogFormat.COLORED,
    log_file: Optional[Union[str, Path]] = None,
    include_context: bool = True,
    json_logs: bool = False
) -> logging.Logger:
    """
    Set up comprehensive logging for Promptix with structured logging capabilities.
    
    Args:
        level: Logging level (can be string like 'INFO' or logging constant)
        format_type: Output format type
        log_file: Optional file path for file logging
        include_context: Whether to include context variables in logs
        json_logs: Force JSON format (overrides format_type)
        
    Returns:
        Configured logger instance
        
    Example:
        >>> logger = setup_logging(level='DEBUG', json_logs=True, log_file='app.log')
        >>> logger.info("Application started", extra={'version': '1.0.0'})
    """
    # Convert string level to integer if needed
    if isinstance(level, str):
        level = getattr(logging, level.upper())
    
    # Handle format type conversion
    if isinstance(format_type, str):
        format_type = LogFormat(format_type.lower())
    
    # Force JSON format if requested
    if json_logs:
        format_type = LogFormat.JSON
    
    # Clear existing handlers to prevent duplicates
    logger = logging.getLogger("promptix")
    logger.handlers.clear()
    logger.propagate = False
    logger.setLevel(level)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = StructuredFormatter(format_type, include_context)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path)
        # Always use JSON format for file logging
        file_formatter = StructuredFormatter(LogFormat.JSON, include_context)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str = "promptix") -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (defaults to 'promptix')
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

def set_context(request_id: Optional[str] = None, user_id: Optional[str] = None, operation: Optional[str] = None) -> None:
    """
    Set context variables for structured logging.
    
    Args:
        request_id: Unique request identifier
        user_id: User identifier
        operation: Current operation name
    """
    if request_id is not None:
        request_id_var.set(request_id)
    if user_id is not None:
        user_id_var.set(user_id)
    if operation is not None:
        operation_var.set(operation)

def clear_context() -> None:
    """Clear all context variables."""
    request_id_var.set(None)
    user_id_var.set(None)
    operation_var.set(None)

# Environment-based configuration
def setup_logging_from_env() -> logging.Logger:
    """
    Set up logging based on environment variables.
    
    Environment variables:
        PROMPTIX_LOG_LEVEL: Log level (default: INFO)
        PROMPTIX_LOG_FORMAT: Format type (colored, json, plain) (default: colored)
        PROMPTIX_LOG_FILE: Log file path (optional)
        PROMPTIX_JSON_LOGS: Force JSON format (true/false) (default: false)
        
    Returns:
        Configured logger instance
    """
    level = os.getenv("PROMPTIX_LOG_LEVEL", "INFO")
    format_type = os.getenv("PROMPTIX_LOG_FORMAT", "colored")
    log_file = os.getenv("PROMPTIX_LOG_FILE")
    json_logs = os.getenv("PROMPTIX_JSON_LOGS", "false").lower() == "true"
    
    return setup_logging(
        level=level,
        format_type=format_type,
        log_file=log_file,
        json_logs=json_logs
    ) 