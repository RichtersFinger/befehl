"""Definitions for class `Argument`."""

from typing import Optional, Callable, Any
import sys


class Argument:
    """CLI-argument."""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        name: str,
        *,
        helptext: Optional[str] = None,
        nargs: Optional[int] = 1,
        parser: Optional[
            Callable[[str], tuple[bool, Optional[str], Optional[Any]]]
        ] = None,
        position: Optional[int] = None,
    ) -> None:
        self.__name = name
        self.__helptext = helptext
        if nargs == 0:
            raise ValueError("Arguments do not support zero 'nargs'.")
        if nargs < 0:
            self.__nargs = -1
        else:
            self.__nargs = nargs
        self.__parser = parser
        self.__position = position

    @property
    def name(self) -> str:
        """Returns `Argument` name."""
        return self.__name

    @property
    def helptext(self) -> Optional[str]:
        """Returns `Argument` helptext."""
        return self.__helptext

    @property
    def nargs(self) -> Optional[int]:
        """Returns `Argument` nargs."""
        return self.__nargs

    @property
    def position(self) -> Optional[int]:
        """Returns `Argument` position."""
        return self.__position

    def parse(self, data: Any):
        """Returns response of `Argument`'s parser if available."""
        if self.__parser:
            ok, msg, data = self.__parser(data)
            if not ok:
                print(msg, file=sys.stderr)
                sys.exit(1)
        return data

    def __repr__(self):
        return (
            f"Option(name={self.name}, helptext={self.helptext}, "
            + f"nargs={self.nargs}, parser={self.__parser}, "
            + f"position={self.position})"
        )

    def __str__(self):
        return self.name
