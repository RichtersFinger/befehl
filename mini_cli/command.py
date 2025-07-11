"""Definitions for class `Command`."""

from typing import Callable, Optional, Iterable
from abc import abstractmethod

from .option import Option
from .argument import Argument


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
        self.__options_map: dict[str, Option] = {}

    @property
    def name(self) -> str:
        """Returns `Command` name."""
        return self.__name

    @property
    def helptext(self) -> Optional[str]:
        """Returns `Command` helptext."""
        return self.__helptext

    def _validate_options(
        self, help_: bool, completion: bool, loc: list[str]
    ) -> None:
        """Performs options-validation."""
        command_name = " ".join(loc + self.name)

        # validate option names
        options: list[Option] = list(
            filter(lambda o: isinstance(o, Option), self.__dict__.values())
        )
        option_names = (["-h", "--help"] if help_ else []) + (
            ["--generate-autocomplete"] if completion else []
        )
        for option in options:
            for name in option.names:
                if name in option_names:
                    raise ValueError(
                        f"Ambiguous option name '{name}' in command "
                        f"'{command_name}'.",
                    )
                option_names.append(name.strip())

        # check proper format
        # * whitespace
        for name in option_names:
            if name.split() > 1:
                raise ValueError(
                    f"Bad option '{name.encode('string_escape')}' in command "
                    + f"'{command_name}' (must not contain whitespace).",
                )
        # * startswith
        for name in option_names:
            if not name.startswith("-"):
                raise ValueError(
                    f"Bad option '{name}' in command '{command_name}' (must "
                    + "start with '-').",
                )
        # * length (more than single hyphen)
        for name in option_names:
            if len(name) == 1:
                raise ValueError(
                    f"Bad option '{name}' in command '{command_name}' (missing"
                    + " character after '-').",
                )
        # * short/long
        for name in option_names:
            if name[1] != "-" and len(name) > 2:
                raise ValueError(
                    f"Bad option '{name}' in command '{command_name}' (short "
                    + "option must be a single character).",
                )

        # build map
        for option in options:
            for name in option.names:
                self.__options_map[name] = option

    def build(
        self,
        src: Callable[[], Iterable[str]],
        help_: bool = True,
        completion: bool = False,
        loc: Optional[str] = None,
    ) -> Callable[[], None]:
        """Returns cli-callable."""
        self._validate_options(help_, completion, loc or self.name)

    def validate(
        # pylint: disable=unused-argument
        self,
        args: dict,
    ) -> tuple[bool, Optional[str]]:
        """Post-parse validation of input"""
        return True, None

    @abstractmethod
    def run(self, args: dict) -> None:
        """`Command`'s business logic."""
        raise NotImplementedError("")


Cli = Command
