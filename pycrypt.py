"""
pycrypt.py encrypts a directory for secure use with git, git-lfs, etc.
"""

import typer
from rich.console import Console
from rich.progress import track
from rich.prompt import Prompt, Confirm
from pathlib import Path
from typing import Optional
from loguru import logger
import sys

# Initialize UX-UI
app = typer.Typer(
    name="poincare",
    help="⚡ Poincare High-Efficiency Data Security Playbook.",
    rich_markup_path=True
)
console = Console()
logger.remove()
logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}", level="INFO")

# Abstraction for interfacing with Rust implementation
# [] TODO: make work
class IEncryptionService:
    """The abstraction layer defining the required encryption contract."""
    def encrypt_directory(self, data_path: Path, key_str: str, output_path: Path) -> float:
        """
        Performs the full compression, hashing, and encryption pipeline.
        Returns the duration in seconds (your efficiency metric).
        """
        raise NotImplementedError

class MockEncryptionService(IEncryptionService):
    """
    A pure Python mock used for TDD, UX/UI testing, and quick debugging.
    It simulates the complexity and speed of the final Rust service.
    """
    def encrypt_directory(self, data_path: Path, key_str: str, output_path: Path) -> float:
        # [] TODO: replace simulation
        logger.info(f"Starting pipeline for: {data_path.name}")

        total_steps = 100
        for step in track(range(total_steps), description="[bold blue]Running security pipeline...[/bold blue]"):
            # Pipeline: Compression (ZSTD), Hashing (SHA256), Encryption (Fernet)
            if step == 20: logger.debug("ZSTD Compression initiated.")
            if step == 50: logger.debug("Integrity Hashing complete.")
            if step == 80: logger.debug("Fernet Encryption initiated.")

            # [] TODO: replace simulation
            import time
            time.sleep(0.01)

        # [] TODO: replace mock data in stages: mock_data directory and then use with real data
        output_path.write_text(f"ENCRYPTED_MOCK_DATA-{key_str}")

        # Return metric for Rust implementation to beat
        # [] TODO: replace initial simulation with actual implementation on the go app created mock_data directory
        duration = 1.05
        logger.success(f"Pipeline complete. Encrypted file: {output_path.name}")

        return duration

# [] TODO: automate command creation using a builder abstraction
@app.command(
    name="encrypt",
    help="🔒 [bold green]Encrypt[/bold green] the target data directory with the Poincare pipeline."
)
def encrypt_cli(
    target_dir: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
        help="The 'data/' directory to encrypt."
    ),
    output_name: str = typer.Option(
        "data.enc", "--out", "-o", help="The name of the final encrypted file."
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Overwrite existing output file without prompting."
    )
):
    """The main CLI entry point for the encryption playbook."""

    # [] TODO: build a UX-UI message generator instead of writing this by hand
    # Note: consider using haskell for easy of composition and focus on pure pipeline
    #   - Can leverage code from haskell blog generator (search for: learning projects in local NAS)
    console.rule("[bold cyan]Poincare Encryption Playbook[/bold cyan]")

    # Note: simulates using a secure key retrieval process
    # [] TODO: automate
    key_input = Prompt.ask("[bold yellow]Enter or generate[/bold yellow] the Fernet Key (or press ENTER to mock)")

    if not key_input:
        key_str = "MOCK_KEY_FOR_TESTING_XXXXXXXXXXXXXXXXXXXXXXX"
        logger.warning("Using mock key. DO NOT use in production.")
    else:
        key_str = key_input

    output_path = target_dir.parent / output_name

    if output_path.exists() and not force:
        if not Confirm.ask(f"⚠️ [bold red]'{output_path.name}' already exists. Overwrite?[/bold red]"):
            logger.info("Operation cancelled by user.")
            raise typer.Exit()

    # [] TODO: consider simplifying if can be done quickly
    service: IEncryptionService = MockEncryptionService()

    try:
        # [] TODO: replace with rust implementation
        duration = service.encrypt_directory(target_dir, key_str, output_path)

        console.rule("[bold green]✅ Pipeline Success[/bold green]")
        console.print(f"Directory: [green]{target_dir.name}[/green] -> File: [green]{output_path.name}[/green]")
        console.print(f"Efficiency Baseline: [bold magenta]{duration:.3f} seconds[/bold magenta] (Target for Rust Optimization)")

        if Confirm.ask("[bold red]RISK ARBITRAGE:[/bold red] Move original directory to trash?"):
            from send2trash import send2trash
            send2trash(str(target_dir))
            logger.warning(f"Moved '{target_dir.name}' to trash.")

    except NotImplementedError:
        console.print("[bold red]FATAL:[/bold red] Core service not implemented. Build the Rust core.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
