#!/usr/bin/env python3

import time
from loguru import logger
from typing import Callable, Any

class PipelineError(Exception):
    """Custom error."""
    # Note: may not be necessary
    pass

class Pipeline:
    """
    Pipeline implementation for python to make it easier to ensure things run as expected.
    It handles timing, logging, and error reporting.
    """
    def __init__(self, step_name: str):
        self.step_name = step_name
        self.start_time = 0.0

    def __enter__(self):
        """Do this before."""
        self.start_time = time.time()
        logger.info(f"[{self.step_name}] Starting execution...")
        # Notes:
        # - context is key to implementation:
            # https://docs.python.org/3/glossary.html#term-context
            # https://peps.python.org/pep-0343/
            # https://www.geeksforgeeks.org/python/context-manager-in-python/
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Do this after."""
        duration = time.time() - self.start_time

        # Expected behavior: build a log of errors and return custom error
        if exc_type is not None:
            logger.error(f"[{self.step_name}] FAILED after {duration:.3f}s. Error: {exc_val}")
            raise PipelineError(f"Step '{self.step_name}' failed.")

        logger.success(f"[{self.step_name}] SUCCESS. Time: {duration:.3f}s")
        return False # Note: should this be True?

def run_step(step_func: Callable[..., Any], **kwargs: Any) -> Any:
    """
    Executes a single function in the pipeline

    Note: may be useful if want to understand stack and heap usage later
    """
    step_name = step_func.__name__

    with Pipeline(step_name) as context:
        # Do f(x) with any number of arguments
        result = step_func(**kwargs)
        return result
