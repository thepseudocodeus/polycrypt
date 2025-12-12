#!/usr/bin/env python3
"""
Hashing

Purpose: Hash directories and files used

Notes:
    - separated into a utility because it become complex
    - used Google style guide to refine: https://google.github.io/styleguide/pyguide.html
"""

import hashlib
from pathlib import Path
from typing import Optional, List, Generator
from loguru import logger

# [] TODO: replace when switch to Go or Rust implementation
DEFAULT_CHUNK_SIZE = 8192

def calculate_file_hash(file_path: Path, chunk_size: int = DEFAULT_CHUNK_SIZE) -> str:
    """
    Use SHA256 hash to validate file hash

    Args:
        file_path: Path to the file to hash
        chunk_size: Size of chunks to read (default: 8192 bytes)

    Returns:
        SHA256 hash digest as hexadecimal string

    Raises:
        FileNotFoundError: If file doesn't exist
        IsADirectoryError: If path is a directory
        IOError: If file cannot be read

    Example:
        >>> hash_value = calculate_file_hash(Path("data.txt"))
        >>> len(hash_value)
        64
    """

    # Note: added to eliminate errors during testing
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if file_path.is_dir():
        raise IsADirectoryError(f"Path is a directory: {file_path}")

    logger.debug(f"Calculating hash for file: {file_path}")
    hasher = hashlib.sha256()

    # [] TODO: consider abstracting into a module that applies try-except as a decorator
    try:
        with file_path.open('rb') as file:
            while chunk := file.read(chunk_size):
                hasher.update(chunk)
    except (IOError, PermissionError) as e:
        logger.error(f"Failed to read file {file_path}: {e}")
        raise IOError(f"Error reading file {file_path}") from e

    hash_result = hasher.hexdigest()
    logger.info(f"File hash calculated: {file_path} -> {hash_result[:8]}...")
    return hash_result

def _hash_directory_contents(directory: Path, exclude_patterns: List[str]) -> Generator[bytes, None, None]:
    """
    Generator that yields hashed content of directory for memory efficiency.

    https://docs.python.org/3/tutorial/classes.html#generators
    """
    all_files = sorted(
        (f for f in directory.rglob('*') if f.is_file()),
        key=lambda p: str(p.relative_to(directory))
    )

    for file_path in all_files:
        if any(pattern in file_path.name for pattern in exclude_patterns):
            logger.debug(f"Skipping excluded file: {file_path}")
            continue

        rel_path = file_path.relative_to(directory)
        yield str(rel_path).encode('utf-8')

        try:
            with file_path.open('rb') as f:
                while chunk := f.read(DEFAULT_CHUNK_SIZE):
                    yield chunk
        except (IOError, PermissionError) as e:
            logger.warning(f"Skipping unreadable file {file_path}: {e}")
            continue

def calculate_directory_hash(
    directory: Path,
    exclude_patterns: Optional[List[str]] = None
) -> str:
    """
    Use SHA256 to hash entire directory.

    Args:
        directory: Path to the directory to hash
        exclude_patterns: List of filename patterns to exclude from hashing

    Returns:
        SHA256 hash digest as hexadecimal string

    Raises:
        FileNotFoundError: If directory doesn't exist
        ValueError: If path is not a directory
        PermissionError: If directory cannot be accessed

    Example:
        >>> hash_value = calculate_directory_hash(Path("project/"))
        >>> len(hash_value)
        64
    """
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    if not directory.is_dir():
        raise ValueError(f"Path is not a directory: {directory}")

    exclude_patterns = exclude_patterns or []
    logger.debug(f"Calculating directory hash for: {directory}")

    hasher = hashlib.sha256()

    try:
        for chunk in _hash_directory_contents(directory, exclude_patterns):
            hasher.update(chunk)
    except PermissionError as e:
        logger.error(f"Permission denied accessing directory: {directory}")
        raise PermissionError(f"Permission denied accessing {directory}") from e

    hash_result = hasher.hexdigest()
    logger.info(f"Directory hash calculated: {directory} -> {hash_result[:8]}...")
    return hash_result

def verify_file_integrity(file_path: Path, expected_hash: str) -> bool:
    """
    Verify file integrity by comparing calculated hash with expected hash.

    Args:
        file_path: Path to the file to verify
        expected_hash: Expected SHA256 hash value

    Returns:
        True if hashes match, False otherwise

    Example:
        >>> is_valid = verify_file_integrity(Path("data.txt"), "abc123...")
    """
    try:
        actual_hash = calculate_file_hash(file_path)
        return actual_hash == expected_hash
    except Exception as e:
        logger.error(f"Integrity verification failed for {file_path}: {e}")
        return False

def _demo_hashing() -> None:
    """Demonstrate hashing functionality with rich output."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.syntax import Syntax

    console = Console()
    console.print(Panel.fit("🔒 [bold cyan]HASHING UTILITIES DEMONSTRATION[/bold cyan]"))

    test_dir = Path("/tmp/hash_demo")
    test_dir.mkdir(exist_ok=True)

    test_file = test_dir / "test_data.txt"
    test_file.write_text("Hello, World! This is test data for hashing.")

    file_hash = calculate_file_hash(test_file)
    console.print(Panel(
        f"📄 [bold]File:[/bold] {test_file.name}\n"
        f"📝 [bold]Content:[/bold] '{test_file.read_text()[:20]}...'\n"
        f"🔒 [bold]SHA256 Hash:[/bold] [green]{file_hash}[/green]",
        title="File Hashing",
        border_style="blue"
    ))

    dir_hash = calculate_directory_hash(test_dir)
    console.print(Panel(
        f"📁 [bold]Directory:[/bold] {test_dir.name}\n"
        f"🔒 [bold]SHA256 Hash:[/bold] [yellow]{dir_hash}[/yellow]",
        title="Directory Hashing",
        border_style="green"
    ))

    import shutil
    shutil.rmtree(test_dir)

if __name__ == "__main__":
    """Allow to demonstrate functionality as script"""
    import sys
    if "--demo" in sys.argv or len(sys.argv) == 1:
        _demo_hashing()
    else:
        print("Usage: python3 -m hashing [--demo]")
