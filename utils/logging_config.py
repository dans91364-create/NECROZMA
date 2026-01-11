#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡🌟💎 ULTRA NECROZMA - LOGGING SYSTEM 💎🌟⚡

Structured logging system
"Every event recorded in the crystal archive"

Technical: Professional logging configuration
- Multiple log levels (DEBUG, INFO, WARNING, ERROR)
- File rotation
- Timestamps and context
- Module-specific loggers
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
import time


# ═══════════════════════════════════════════════════════════════
# 🔧 LOG FORMATTER
# ═══════════════════════════════════════════════════════════════

class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record):
        # Add color to level name
        if record.levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[record.levelname]}"
                f"{record.levelname}"
                f"{self.COLORS['RESET']}"
            )
        
        return super().format(record)


# ═══════════════════════════════════════════════════════════════
# 🌟 LOGGER SETUP
# ═══════════════════════════════════════════════════════════════

def setup_logger(name="necrozma", level="INFO", log_dir="logs",
                log_to_file=True, log_to_console=True):
    """
    Setup structured logger
    
    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        log_dir: Directory for log files
        log_to_file: Enable file logging
        log_to_console: Enable console logging
        
    Returns:
        logging.Logger: Configured logger
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    logger.handlers = []
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # File handler (with rotation)
    if log_to_file:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        log_file = log_path / f"{name}_{timestamp}.log"
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    return logger


# ═══════════════════════════════════════════════════════════════
# 🎯 PERFORMANCE LOGGER
# ═══════════════════════════════════════════════════════════════

class PerformanceLogger:
    """Context manager for logging performance metrics"""
    
    def __init__(self, logger, operation_name):
        """
        Initialize performance logger
        
        Args:
            logger: Logger instance
            operation_name: Name of operation to time
        """
        self.logger = logger
        self.operation_name = operation_name
        self.start_time = None
    
    def __enter__(self):
        """Start timing"""
        self.start_time = time.time()
        self.logger.info(f"Starting: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End timing and log"""
        elapsed = time.time() - self.start_time
        
        if exc_type is None:
            self.logger.info(
                f"Completed: {self.operation_name} in {elapsed:.2f}s"
            )
        else:
            self.logger.error(
                f"Failed: {self.operation_name} after {elapsed:.2f}s - {exc_val}"
            )
        
        return False  # Don't suppress exceptions


# ═══════════════════════════════════════════════════════════════
# 📊 PROGRESS LOGGER
# ═══════════════════════════════════════════════════════════════

class ProgressLogger:
    """Logger with progress tracking"""
    
    def __init__(self, logger, total_items, description="Processing"):
        """
        Initialize progress logger
        
        Args:
            logger: Logger instance
            total_items: Total number of items to process
            description: Description of operation
        """
        self.logger = logger
        self.total_items = total_items
        self.description = description
        self.current = 0
        self.start_time = time.time()
        self.last_log_time = self.start_time
        self.log_interval = 5.0  # Log every 5 seconds
    
    def update(self, n=1):
        """
        Update progress
        
        Args:
            n: Number of items processed
        """
        self.current += n
        current_time = time.time()
        
        # Log at intervals
        if current_time - self.last_log_time >= self.log_interval:
            self._log_progress()
            self.last_log_time = current_time
    
    def _log_progress(self):
        """Log current progress"""
        if self.total_items > 0:
            percent = (self.current / self.total_items) * 100
            elapsed = time.time() - self.start_time
            
            if self.current > 0:
                rate = self.current / elapsed
                remaining = (self.total_items - self.current) / rate
                
                self.logger.info(
                    f"{self.description}: {self.current}/{self.total_items} "
                    f"({percent:.1f}%) - {rate:.1f} items/s - "
                    f"ETA: {remaining:.1f}s"
                )
            else:
                self.logger.info(
                    f"{self.description}: {self.current}/{self.total_items} "
                    f"({percent:.1f}%)"
                )
    
    def finish(self):
        """Log final statistics"""
        elapsed = time.time() - self.start_time
        if self.total_items > 0:
            rate = self.total_items / elapsed
            self.logger.info(
                f"{self.description}: Completed {self.total_items} items "
                f"in {elapsed:.2f}s ({rate:.1f} items/s)"
            )


# ═══════════════════════════════════════════════════════════════
# 🎯 DEFAULT LOGGER
# ═══════════════════════════════════════════════════════════════

# Default logger instance
_default_logger = None


def get_logger(name="necrozma", **kwargs):
    """
    Get or create logger
    
    Args:
        name: Logger name
        **kwargs: Additional arguments for setup_logger
        
    Returns:
        logging.Logger: Logger instance
    """
    global _default_logger
    
    if _default_logger is None:
        _default_logger = setup_logger(name, **kwargs)
    
    return _default_logger
