#!/usr/bin/env python3
"""
Custom PyCrypter Exceptions

Purpose: Use an exception heirarchy to make debugging more intuitive
"""

class UtilsError(Exception):
    """Base exception for all utilities errors."""
    pass

class HashingError(UtilsError):
    """Exceptions related to hashing operations."""
    pass

class FileAccessError(UtilsError):
    """Exceptions related to file access issues."""
    pass

class ConfigurationError(UtilsError):
    """Exceptions related to configuration issues."""
    pass

class ValidationError(UtilsError):
    """Exceptions related to input validation."""
    pass
