#!/usr/bin/env python3
"""
Logging that works.

Initial logging approach used in 'logging.py' results in multiple serialization errors. I need to complete this tool to use in a portfolio.
Now, I will create a multiple logging approach using tool so I can be confident in the final implementation.
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Callable, Protocol
from enum import Enum
from contextlib import contextmanager

# Implementing threading to leverage system resources
import threading

class LogBackend(Protocol):
    """Python interface to allow interchanging loggers as it needed.
    https://typing.python.org/en/latest/spec/protocol.html
    """
    def log(self, level: str, message: str, context: Dict[str, Any]) -> bool:
        """True = logging successful, False = errors encountered."""
        ...


# implement loguru again but with fallback options
class LoguruBackend:
  """Loguru backend - preferred."""

  def __init__(self, format_type: str = "console"):
      try:
          from loguru import logger
          logger.remove()

          if format_type == "console":
              logger.add(
                  sys.stderr,
                  format=(
                      "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                      "<level>{level: <8}</level> | "
                      "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                      "<level>{message}</level>"
                  ),
                  colorize=True,
              )
          self._logger = logger
          self._available = True
      except Exception as e:
          print(f"Loguru initialization failed: {e}", file=sys.stderr)
          self._available = False

  def log(self, level: str, message: str, context: Dict[str, Any]) -> bool:
      if not self._available:
          return False

      try:
          log_method = getattr(self._logger, level.lower())
          log_method(message, extra=context)
          return True
      except Exception:
          return False


class StandardLibBackend:
    """If there's a problem consider using built-in logging."""

    def __init__(self, log_file: Optional[Path] = None, format_type: str = "json"):
        self._logger = logging.getLogger("app")
        self._logger.setLevel(logging.DEBUG)

        if format_type == "json":
            formatter = self._json_formatter()
        else:
            formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s'
            )

        if log_file:
            handler = logging.FileHandler(log_file)
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)
        else:
            handler = logging.StreamHandler(sys.stderr)
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)

    def _json_formatter(self):
        class JSONFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    'timestamp': datetime.utcfromtimestamp(record.created).isoformat(),
                    'level': record.levelname,
                    'message': record.getMessage(),
                    'logger': record.name,
                    'function': record.funcName,
                    'line': record.lineno,
                }

                # Ensure we don't lose context
                if hasattr(record, 'context'):
                    log_entry['context'] = record.context

                return json.dumps(log_entry)

        return JSONFormatter()

    def log(self, level: str, message: str, context: Dict[str, Any]) -> bool:
        try:
            log_method = getattr(self._logger, level.lower())

            # extra = context
            extra = {'context': context} if context else {}
            log_method(message, extra=extra)
            return True
        except Exception:
            return False


class DirectFileBackend:
    """If all else fails, write to a file directly using python file writing pattern."""

    def __init__(self, log_file: Path):
        self.log_file = log_file
        self._lock = threading.Lock()

        # resolved issue with directory not existing
        try:
            log_file.parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

    def log(self, level: str, message: str, context: Dict[str, Any]) -> bool:
        try:
            with self._lock:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    entry = {
                        'timestamp': datetime.utcnow().isoformat(),
                        'level': level,
                        'message': message,
                        'context': context
                    }
                    f.write(json.dumps(entry) + '\n')
            return True
        except Exception:
            return False


class StderrBackend:
    """Directly present errors to system API (?)."""

    def log(self, level: str, message: str, context: Dict[str, Any]) -> bool:
        try:
            timestamp = datetime.utcnow().isoformat()
            ctx_str = f" {context}" if context else ""
            print(f"{timestamp} | {level: <8} | {message}{ctx_str}", file=sys.stderr)
            return True
        except Exception:
            return False


class SecuritySanitizer:
    """Don't log PII or SPII."""

    # [] TODO: use a yaml file to track these
    SENSITIVE_KEYS = {
        'password', 'passwd', 'pwd', 'secret', 'token', 'api_key',
        'apikey', 'auth', 'credential', 'private_key', 'access_token',
        'session_id', 'ssn', 'credit_card', 'cvv'
    }

    @classmethod
    def sanitize_message(cls, message: str) -> str:
        """Remove newlines and control characters to prevent log injection."""
        if not isinstance(message, str):
            message = str(message)

        message = message.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')

        if len(message) > 10000:
            message = message[:10000] + "... (truncated)"

        return message

    @classmethod
    def sanitize_context(cls, context: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive information keys."""
        if not context:
            return {}

        sanitized = {}
        for key, value in context.items():
            if any(sensitive in key.lower() for sensitive in cls.SENSITIVE_KEYS):
                sanitized[key] = "***REDACTED***"
            else:
                if isinstance(value, dict):
                    sanitized[key] = cls.sanitize_context(value)
                else:
                    sanitized[key] = value

        return sanitized


class Logger:
    """
    Logger with fallback to overcome challenge of getting loguru to work.
    """

    def __init__(
        self,
        log_file: Optional[Path] = None,
        console_format: str = "console",
        file_format: str = "json",
        enable_security: bool = True
    ):
        self.log_file = log_file
        self.enable_security = enable_security
        self._backends = []
        self._failed_backends = set()
        self._setup_backends(console_format, file_format)

    def _setup_backends(self, console_format: str, file_format: str):
        """Setup loggers."""

        try:
            backend = LoguruBackend(console_format)
            self._backends.append(("loguru_console", backend))
        except Exception as e:
            print(f"Loguru console setup failed: {e}", file=sys.stderr)

        if self.log_file:
            try:
                backend = StandardLibBackend(self.log_file, file_format)
                self._backends.append(("stdlib_file", backend))
            except Exception as e:
                print(f"Stdlib file logging setup failed: {e}", file=sys.stderr)

        if self.log_file:
            try:
                backend = DirectFileBackend(self.log_file)
                self._backends.append(("direct_file", backend))
            except Exception as e:
                print(f"Direct file backend setup failed: {e}", file=sys.stderr)

        # [] TODO: discover way to escalate this because this is the last resort
        self._backends.append(("stderr", StderrBackend()))

        if not self._backends:
            raise RuntimeError("CRITICAL: All logging backends failed to initialize")

    def _log(self, level: str, message: str, **context):
        """Core logging method with defense in depth."""

        if self.enable_security:
            message = SecuritySanitizer.sanitize_message(message)
            context = SecuritySanitizer.sanitize_context(context)

        logged = False
        for name, backend in self._backends:
            if name in self._failed_backends:
                continue

            try:
                # When one works move on
                if backend.log(level, message, context):
                    logged = True
                    break
            except Exception as e:
                self._failed_backends.add(name)
                self._meta_log(f"Backend {name} failed: {e}")

        if not logged:
            # Note: this should be unreachable code. Escalate.
            try:
                print(f"CRITICAL: All logging failed for: {message}", file=sys.stderr)
            except Exception:
                pass

    def _meta_log(self, message: str):
        """Log logging problems encountered."""
        try:
            print(f"[LOGGING SYSTEM] {message}", file=sys.stderr)
        except Exception:
            pass

    def debug(self, message: str, **context):
        self._log("DEBUG", message, **context)

    def info(self, message: str, **context):
        self._log("INFO", message, **context)

    def warning(self, message: str, **context):
        self._log("WARNING", message, **context)

    def error(self, message: str, **context):
        self._log("ERROR", message, **context)

    def critical(self, message: str, **context):
        self._log("CRITICAL", message, **context)

    @contextmanager
    def context(self, **context_vars):
        """
        Borrowed from python documentation.

        [] TODO: insert link to python documentation sources

        Usage:
            with logger.context(request_id="123", user_id="456"):
                logger.info("Processing request")
                # All logs here will include request_id and user_id
        """

        original_log = self._log

        def wrapped_log(level: str, message: str, **kwargs):
            merged_context = {**context_vars, **kwargs}
            original_log(level, message, **merged_context)

        self._log = wrapped_log
        try:
            yield
        finally:
            self._log = original_log


def log_execution_time(logger: Logger):
    """Using builder (factory) pattern to add timing."""
    def decorator(func: Callable) -> Callable:
        from functools import wraps
        import time

        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            logger.debug(f"Starting {func.__name__}")

            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start
                logger.debug(
                    f"Completed {func.__name__}",
                    execution_time_seconds=elapsed
                )
                return result
            except Exception as e:
                elapsed = time.time() - start
                logger.error(
                    f"Failed {func.__name__}",
                    execution_time_seconds=elapsed,
                    error=str(e)
                )
                raise

        return wrapper
    return decorator


if __name__ == "__main__":
    # 1. make logger
    logger = Logger(
        log_file=Path("/tmp/demo.log"),
        console_format="console",
        file_format="json",
        enable_security=True
    )

    print("=" * 60)
    print("LOGGING SYSTEM DEMO")
    print("=" * 60)

    # 2. show core logging
    print("\n1. Basic Logging:")
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")

    # 3. add structured logging
    print("\n2. Structured Logging:")
    logger.info("User login", user_id=123, ip_address="192.168.1.1")

    # 4. test sensitive info functionality
    print("\n3. Security - Sensitive Data Redaction:")
    logger.info("Auth attempt", username="alice", password="secret123", token="abc123")

    # 5. add context management functionality
    print("\n4. Context Manager:")
    with logger.context(request_id="req-456", user_id="user-789"):
        logger.info("Processing request")
        logger.info("Request completed")

    # 6. Time execution
    print("\n5. Execution Timing:")
    @log_execution_time(logger)
    def slow_operation():
        import time
        time.sleep(0.1)
        return "done"

    slow_operation()

    # 7. add in security functionality
    print("\n6. Security - Log Injection Prevention:")
    malicious_input = "normal message\n[FORGED LOG ENTRY] level=ERROR msg=hacked"
    logger.info(malicious_input)

    print("\n" + "=" * 60)
    print("✅ Demo completed. Check /tmp/demo.log for JSON output")
    print("=" * 60)
