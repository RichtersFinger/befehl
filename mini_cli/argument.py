"""Definitions for class `Argument`."""

from typing import Optional, Callable, Any
import sys


class Argument:
    """
    CLI-argument class.

    Keyword arguments:
    name -- argument name
    helptext -- argument description for auto-generated help-option
                (defeault None)
    nargs -- number of accepted values; a negative value is equivalent
             to any number of values
             (default 1)
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
    position -- manually control `Argument` position in the context of a
                `Command` (note that in a single `Command`, either all
                or no `Arguments` should receive this keyword)
                (default None, order in which `Argument`s are defined)
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        name: str,
        *,
        helptext: Optional[str] = None,
        nargs: int = 1,
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
            f"Argument(name={self.name}, helptext={self.helptext}, "
            + f"nargs={self.nargs}, parser={self.__parser}, "
            + f"position={self.position})"
        )

    def __str__(self):
        return self.name
