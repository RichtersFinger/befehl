"""Definitions for class `Option`."""

from typing import Iterable, Optional, Callable, Any
import sys

from .common import quote_list


class Option:
    """
    CLI-option class.

    Keyword arguments:
    names -- option name(s)
    helptext -- option description for auto-generated help-option
                (defeault None)
    nargs -- number of accepted values; a negative value is equivalent
             to any number of values
             (default 0)
    strict -- if `True`, a command will exit with an error if the number
              of user-provided values is lower than `nargs`
              (default True)
    parser -- custom parser-function for individual values

              Should accept a value as string and return a tuple of
              boolean (value ok), string (message if rejected), and
              parsed data. For example to parse as integer:
              ```
              def parse_int(data):
                try:
                  number = int(data)
                except ValueError:
                  return False, f"input '{data}' is not an integer", None
                return True, None, number
              ```

              (default None)
    """

    def __init__(
        self,
        names: str | Iterable[str],
        *,
        helptext: Optional[str] = None,
        nargs: Optional[int] = 0,
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
        self.__names = (names,) if isinstance(names, str) else names
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

    def __repr__(self):
        return (
            f"Option(names={self.names}, helptext={self.helptext}, "
            + f"nargs={self.nargs}, strict={self.strict}, "
            + f"parser={self.__parser})"
        )

    def __str__(self):
        return quote_list(self.names)
