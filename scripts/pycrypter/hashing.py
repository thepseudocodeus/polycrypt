#!/usr/bin/env python3
"""
Collection of shared functions which can be used across the app

Notes:
    - ensure packages used here are in main python environment
    - use taskfile to run from main environment
    - use uv to simplify use
"""

import hashlib
from pathlib import Path
import os

def calculate_directory_hash(directory: Path) -> str:
    """Calculates a consistent SHA256 hash of all file contents and names."""
    hasher = hashlib.sha256()
    for root, _, files in os.walk(directory):
        for name in sorted(files):
            file_path = Path(root) / name
            hasher.update(str(file_path.relative_to(directory)).encode())
            try:
                with open(file_path, 'rb') as f:
                    hasher.update(f.read())
            except IOError: continue
    return hasher.hexdigest()

def calculate_file_hash(file_path: Path) -> str:
    """Calculates SHA256 hash for a single file's content."""
    hasher = hashlib.sha256()
    with file_path.open('rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()


if __name__ == "__main__":
    from pathlib import Path

    # make directory
    script_dir = Path(__file__).parent
    tmp_path = script_dir / "tmp"
    tmp_path.mkdir(parents=True, exist_ok=True)


    # put file in it
    tmp_file = Path("temp_demo_file.txt")
    tmp_file_path = tmp_path / tmp_file
    tmp_file.write_text("Hello World!")

    fhash_value = calculate_file_hash(tmp_file)

    print("-" * 30)
    print(f"File: {tmp_file.name}")
    print(f"Content: '{tmp_file.read_text()}'")
    print(f"Calculated Hash: {fhash_value}")
    print("NOTE: This hash MUST match the expected value in test_hashing.py.")
    print("-" * 30)

    dhash_value = calculate_directory_hash(tmp_path)

    print("-" * 30)
    print(f"File: {tmp_file.name}")
    print(f"Content: '{tmp_file.read_text()}'")
    print(f"Calculated Hash: {fhash_value}")
    print("NOTE: This hash MUST match the expected value in test_hashing.py.")
    print("-" * 30)


    tmp_file.unlink()
    tmp_path.unlink()
