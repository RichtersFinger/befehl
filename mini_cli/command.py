"""Definitions for class `Command`."""

from typing import Callable, Optional, Iterable, Any
from abc import abstractmethod
import sys

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
        self.__arguments_map: dict[int, Argument] = {}
        self.__subcommands: dict[
            str, Callable[[Optional[Iterable[str]]], None]
        ] = {}

    @property
    def name(self) -> str:
        """Returns `Command` name."""
        return self.__name

    @property
    def helptext(self) -> Optional[str]:
        """Returns `Command` helptext."""
        return self.__helptext

    def _validate_options(
        self, help_: bool, completion: bool, command_name: str
    ) -> None:
        """Performs options-validation."""
        # collect options
        options: list[Option] = list(
            filter(lambda o: isinstance(o, Option), self.__dict__.values())
        )
        if len(options) == 0:
            return

        option_names = (["-h", "--help"] if help_ else []) + (
            ["--generate-autocomplete"] if completion else []
        )

        # uniqueness + collect names
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
                self.__options_map[name.strip()] = option

    def _validate_arguments(self, command_name: str) -> None:
        """Performs arguments-validation."""
        # collect arguments
        arguments: list[Argument] = list(
            filter(lambda o: isinstance(o, Argument), self.__dict__.values())
        )
        if len(arguments) == 0:
            return

        # check
        # * nargs<0 cannot be combined
        if len(arguments) > 1:
            bad_arg = next((arg for arg in arguments if arg.nargs < 0), None)
            if bad_arg is not None:
                raise ValueError(
                    f"Bad argument '{bad_arg.name}' in command "
                    + f"'{command_name}' (unlimited 'nargs' must not be "
                    + "combined with other arguments)."
                )

        # * none or all arguments have position
        if len(arguments) > 1:
            bad_arg = next(
                (
                    arg
                    for arg in arguments
                    if (arg.position is None)
                    is (arguments[0].position is None)
                ),
                None,
            )
            if bad_arg is not None:
                raise ValueError(
                    f"Bad arguments in command '{command_name}' (either "
                    + "all arguments or none must get 'position'-keyword)."
                )

        # * duplicate positions
        if arguments[0].position is not None:
            positions = []
            for argument in arguments:
                if argument.position in positions:
                    raise ValueError(
                        f"Bad arguments in command '{command_name}' (conflict "
                        + f"for position '{argument.position}')."
                    )
                positions.append(argument.position)

        # build map
        self.__arguments_map.update(
            dict(
                enumerate(
                    arguments
                    if arguments[0].position is not None
                    else sorted(arguments, lambda a: a.position)
                )
            )
        )

    def _validate_subcommands(
        self, help_: bool, completion: bool, command_name: str
    ) -> None:
        """Performs subcommand-validation."""
        commands: list["Command"] = list(
            filter(lambda o: isinstance(o, Command), self.__dict__.values())
        )
        if len(commands) == 0:
            return

        # check
        # * duplicate names
        command_names = []
        for command in commands:
            if command.name in command_names:
                raise ValueError(
                    f"Ambiguous subcommand '{command.name}' in command "
                    + f"'{command_name}'."
                )
            command_names.append(command.name.strip())
        # * whitespace
        for name in command_names:
            if name.split() > 1:
                raise ValueError(
                    f"Bad subcommand '{name.encode('string_escape')}' in "
                    + f"command '{command_name}' (must not contain "
                    + "whitespace).",
                )
        # * leading character
        for name in command_names:
            if name.startswith("-"):
                raise ValueError(
                    f"Bad subcommand '{name}' in command '{command_name}' "
                    + "(must not start with '-').",
                )

        # build map
        for command in commands:
            self.__options_map[command.name.strip()] = command.build(
                help_, completion, command_name
            )

    def _parse(self, raw: Iterable[str]) -> dict[str, Any]:
        """Parse given raw input."""
        # TODO
        return {}

    def build(
        self,
        help_: bool = True,
        completion: bool = False,
        *,
        loc: Optional[str] = None,
    ) -> Callable[[Optional[Iterable[str]]], None]:
        """Returns cli-callable."""
        # prepare
        if loc is None:
            command_name = self.name.strip()
        else:
            command_name = loc + f" {self.name.strip()}"

        # validate and build components
        self._validate_options(help_, completion, command_name)
        self._validate_arguments(command_name)
        self._validate_subcommands(help_, completion, command_name)

        # define command logic
        def command(raw: Optional[Iterable[str]]) -> None:
            # load raw input
            if raw is None:
                raw = sys.argv[1:]

            # determine subcommand
            if raw[0] in self.__subcommands:
                self.__subcommands[raw[0]](raw[1:])

            # parse
            args = self._parse(raw)

            # help
            # TODO

            # generate autocomplete
            # TODO

            # validate
            ok, msg = self.validate(args)
            if not ok:
                print(msg, file=sys.stderr)
                sys.exit(1)

            # run
            self.run(args)

        return command

    def validate(
        # pylint: disable=unused-argument
        self,
        args: dict[str, Any],
    ) -> tuple[bool, Optional[str]]:
        """Post-parse validation of input"""
        return True, None

    @abstractmethod
    def run(self, args: dict[str, Any]) -> None:
        """`Command`'s business logic."""
        raise NotImplementedError("")


Cli = Command
