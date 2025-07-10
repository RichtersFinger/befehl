"""Definitions for class `Command`."""

from typing import Callable, Optional
from abc import abstractmethod


class Command:
    """CLI-command."""

    def __init__(
        self,
        name: str,
        *,
        helptext: Optional[str] = None,
    ) -> None:
        self.__name = name
        self.__helptext = helptext

    @property
    def name(self) -> str:
        """Returns `Command` name."""
        return self.__name

    @property
    def helptext(self) -> Optional[str]:
        """Returns `Command` helptext."""
        return self.__helptext

    def build(self, **kwargs) -> Callable[[], None]:
        """Builds a cli from this command."""
        # TODO:
        # src=lambda: sys.argv[1:], completion=True, help=True
        return kwargs

    def validate(
        # pylint: disable=unused-argument
        self, args: dict
    ) -> tuple[bool, Optional[str]]:
        """Post-parse validation of input"""
        return True, None

    @abstractmethod
    def run(self, args: dict) -> None:
        """`Command`'s business logic."""
        raise NotImplementedError("")


Cli = Command
