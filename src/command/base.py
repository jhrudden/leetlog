from abc import ABC, abstractmethod
from argparse import ArgumentParser, Namespace
from typing import Callable


class Command(ABC):
    """Base class for all CLI commands."""

    def __init__(self, args: Namespace):
        """
        Initialize command with parsed arguments.

        Args:
            args: Parsed command-line arguments
        """
        self.args = args

    @classmethod
    @abstractmethod
    def init_parser(cls, parser_builder: Callable[[str, str], ArgumentParser]) -> None:
        """
        Initialize the parser using the provided parser builder function.

        Args:
            parser_builder: Function that takes (name, help) and returns an ArgumentParser

        TODO: Implement in subclasses.
        """
        raise NotImplementedError("Subclasses must implement init_parser")

    @abstractmethod
    def __call__(self) -> None:
        """
        Execute the command.

        TODO: Implement in subclasses.
        """
        raise NotImplementedError("Subclasses must implement __call__")
