#!/usr/bin/env python3

import typer
from rich.console import Console
from pathlib import Path
from loguru import logger
import sys
import time

from pipeline import run_step, PipelineError

# Setup app
app = typer.Typer(name="pycrypter", help="Secure Data Encryption Play.")
console = Console()
logger.remove(); logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}", level="INFO")

if __name__ == "__main__":
    app()
