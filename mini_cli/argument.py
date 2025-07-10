"""Definitions for class `Argument`."""

from typing import Optional, Callable, Any


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

    def parse(self, data: Any) -> tuple[bool, Optional[str], Any]:
        """Returns response of `Argument`'s parser if available."""
        if self.__parser:
            return self.__parser(data)
        return True, None, data
