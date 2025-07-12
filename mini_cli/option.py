"""Definitions for class `Option`."""

from typing import Iterable, Optional, Callable, Any
import sys


class Option:
    """CLI-option."""

    def __init__(
        self,
        names: Iterable[str],
        *,
        helptext: Optional[str] = None,
        nargs: Optional[int] = 1,
        strict: bool = True,
        parser: Optional[
            Callable[[str], tuple[bool, Optional[str], Optional[Any]]]
        ] = None,
    ) -> None:
        if len(names) == 0:
            raise ValueError("An Option requires at least one name.")
        if nargs < 0:
            raise ValueError(
                "Options do not support negative values for 'nargs'."
            )
        self.__names = names
        self.__helptext = helptext
        self.__nargs = nargs
        self.__strict = strict
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

    @property
    def strict(self) -> bool:
        """Returns `Option` strict."""
        return self.__strict

    def parse(self, data: Any) -> Any:
        """Returns response of `Option`'s parser if available."""
        if self.__parser:
            ok, msg, data = self.__parser(data)
            if not ok:
                print(msg, file=sys.stderr)
                sys.exit(1)
        return data
