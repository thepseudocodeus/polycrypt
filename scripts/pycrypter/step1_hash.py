# poincare_app/pipeline/p1_hash_source.py
from pathlib import Path
from .hashing import calculate_directory_hash
from .adv_logging import Logger

logger = Logger(
    log_file=Path("/tmp/demo.log"),
    console_format="console",
    file_format="json",
    enable_security=True
)

def hash_source(source_dir: Path) -> str:
    """
    P1: Calculates the H_original hash for the entire source directory.
    This is the non-negotiable Source of Truth.
    """
    logger.info("P1: Calculating H_original...")
    h_original = calculate_directory_hash(source_dir)
    logger.info(f"P1: H_original established: {h_original[:12]}...")
    return h_original

if __name__ == "__main__":
    import os
    import sys

    if len(sys.argv) > 1:
        source_path_str = sys.argv[1]
    else:
        source_path_str = "mock_data"

    source_path = Path(source_path_str).resolve()

    if not source_path.is_dir():
        project_root_path = Path(os.getcwd()) / source_path_str
        if project_root_path.is_dir():
            source_path = project_root_path
        else:
            logger.error(f"Directory '{source_path_str}' not found at current location or project root.")
            sys.exit(1)

    result = ""

    try:
        result = hash_source(source_path)
    except Exception as e:
        print(f"Error: {e}")

    print(f"Hash of{source_path} = {result}")
