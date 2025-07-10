"""Definitions for class `Option`."""

from typing import Iterable, Optional, Callable, Any


class Option:
    """CLI-option."""

    def __init__(
        self,
        names: Iterable[str],
        *,
        helptext: Optional[str] = None,
        nargs: Optional[int] = 1,
        parser: Optional[
            Callable[[str], tuple[bool, Optional[str], Optional[Any]]]
        ] = None,
    ) -> None:
        self.__names = names
        self.__helptext = helptext
        self.__nargs = nargs
        self.__parser = parser

    @property
    def names(self) -> Optional[Iterable[str]]:
        """Returns `Option` names."""
        return self.__names

    @property
    def helptext(self) -> Optional[str]:
        """Returns `Option` helptext."""
        return self.__helptext

    @property
    def nargs(self) -> Optional[int]:
        """Returns `Option` nargs."""
        return self.__nargs

    def parse(self, data: Any) -> tuple[bool, Optional[str], Any]:
        """Returns response of `Option`'s parser if available."""
        if self.__parser:
            return self.__parser(data)
        return True, None, data
