import argparse
from abc import ABC, abstractmethod


class Command(ABC):
    """Base class for all CLI commands."""

    def __init__(self, args: argparse.Namespace):
        """
        Initialize command with parsed arguments.

        Args:
            args: Parsed command-line arguments
        """
        self.args = args

    @abstractmethod
    def __call__(self) -> None:
        """
        Execute the command.

        TODO: Implement in subclasses.
        """
        raise NotImplementedError("Subclasses must implement __call__")
