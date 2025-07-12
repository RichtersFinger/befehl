"""Definitions for class `Command`."""

from typing import Callable, Optional, Iterable, Any
from abc import abstractmethod
import sys
import os
from itertools import zip_longest

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
        self.__help_option = Option(
            ("-h", "--help"),
            helptext="Output this message and exit.",
            nargs=0,
        )
        self.__autocomplete_option = Option(
            ("--generate-autocomplete"),
            helptext="...",
            nargs=0,
        )
        self.__options_map: dict[str, Option] = {}
        self.__arguments_list: list[Argument] = []
        self.__subcommands: dict[
            str, tuple[Command, Callable[[Optional[Iterable[str]]], None]]
        ] = {}

    @property
    def name(self) -> str:
        """Returns `Command` name."""
        return self.__name

    @property
    def helptext(self) -> Optional[str]:
        """Returns `Command` helptext."""
        return self.__helptext

    def __str__(self):
        return f"Command(name={self.name}, helptext={self.helptext})"

    def _validate_options(
        self, help_: bool, completion: bool, command_name: str
    ) -> None:
        """Performs options-validation."""
        # collect options
        options: list[Option] = list(
            filter(
                lambda o: isinstance(o, Option),
                self.__class__.__dict__.values(),
            )
        )

        if help_:
            options.append(self.__help_option)

        if completion:
            options.append(self.__autocomplete_option)

        if len(options) == 0:
            return

        option_names = []

        # uniqueness + collect names
        for option in options:
            for name in option.names:
                if name in option_names:
                    raise ValueError(
                        f"Ambiguous name '{name}' in option {option} of "
                        f"command '{command_name}'.",
                    )
                option_names.append(name.strip())

        # check proper format
        # * whitespace
        for name in option_names:
            if len(name.split()) > 1:
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
        # * -- not allowed
        for name in option_names:
            if name == "--":
                raise ValueError(
                    f"Bad option '{name}' in command '{command_name}' (must "
                    + "not equal '--').",
                )
        # * = not allowed
        for name in option_names:
            if "=" in name:
                raise ValueError(
                    f"Bad option '{name}' in command '{command_name}' (must "
                    + "not contain '=').",
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
            filter(
                lambda o: isinstance(o, Argument),
                self.__class__.__dict__.values(),
            )
        )
        if len(arguments) == 0:
            return

        # check
        # * nargs<0 cannot be combined with any other
        if len(arguments) > 1:
            bad_arg = next((arg for arg in arguments if arg.nargs < 0), None)
            if bad_arg is not None:
                raise ValueError(
                    f"Bad argument '{bad_arg}' in command '{command_name}' "
                    + "(unlimited 'nargs' must not be combined with other "
                    + "arguments)."
                )

        # * none or all arguments have position
        if len(arguments) > 1:
            bad_arg = next(
                (
                    arg
                    for arg in arguments
                    if (arg.position is None)
                    is not (arguments[0].position is None)
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
        self.__arguments_list.extend(
            arguments
            if arguments[0].position is not None
            else sorted(arguments, key=lambda a: a.position)
        )

    def _validate_subcommands(
        self,
        help_: bool,
        completion: bool,
        command_name: str,
    ) -> None:
        """Performs subcommand-validation."""
        commands: list["Command"] = list(
            filter(
                lambda o: isinstance(o, Command),
                self.__class__.__dict__.values(),
            )
        )
        if len(commands) == 0:
            return

        # check
        # * duplicate names
        command_names = []
        for command in commands:
            if command.name in command_names:
                raise ValueError(
                    f"Ambiguous subcommand '{command}' in command "
                    + f"'{command_name}'."
                )
            command_names.append(command.name.strip())
        # * whitespace
        for name in command_names:
            if len(name.split()) > 1:
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
            self.__subcommands[command.name.strip()] = (
                command,
                command.build(help_, completion, loc=command_name),
            )

    def _parse_preprocess_options(
        self, raw: Iterable[str]
    ) -> list[Option | str]:
        """
        Returns pre-processed raw-input.

        Pre-processing options consists of
        * validating requirements
          * not allowed characters
          * unknown options
          * ..
        * resolve input with '='-syntax or grouped short-options
        * replaces option-names with Option-instances
          * respects '--'-separator for options and arguments
        """
        preprocessed = []
        post_options = False
        for arg in raw:
            if arg == "--":
                post_options = True
                preprocessed.append(arg)
                continue

            # resolve options with '=' if needed
            if not post_options and "=" in arg:
                op, value = arg.split("=", maxsplit=1)
                if op in self.__options_map:
                    preprocessed.extend([self.__options_map[op], value])
                    continue

            # resolve grouped short options
            if (
                not post_options
                and len(arg) > 2
                and arg[0] == "-"
                and arg[1] != "-"
            ):
                if "=" in arg:
                    print(
                        "Syntax '<option-group>=<value>' not allowed",
                        file=sys.stderr,
                    )
                    sys.exit(1)
                split = list(map(lambda s: f"-{s}", arg[1:]))
                for op in split:
                    if op not in self.__options_map:
                        print(f"Unknown option '{op}'", file=sys.stderr)
                        sys.exit(1)
                    if (
                        self.__options_map[op].nargs > 0
                        and self.__options_map[op].strict
                    ):
                        print(
                            f"Missing arguments for option '{op}'",
                            file=sys.stderr,
                        )
                        sys.exit(1)
                    preprocessed.append(self.__options_map[op])
                continue

            # unknown options
            if (
                not post_options
                and arg.startswith("-")
                and arg not in self.__options_map
            ):
                print(
                    f"Unknown option '{arg}'",
                    file=sys.stderr,
                )
                sys.exit(1)

            # regular option
            if not post_options and arg in self.__options_map:
                preprocessed.append(self.__options_map[arg])
                continue

            # regular argument
            preprocessed.append(arg)

        return preprocessed

    def _parse_postprocess_options(self, result: dict[str, list[Any]]) -> None:
        """
        Post-processing options consists of
        * validating violation of strict-options
        """

        # handle bad number of args for options
        for option, values in result.items():
            option = self.__options_map[option]
            # validate strict options
            if option.strict and len(values) != option.nargs:
                print(
                    f"Option '{option.names[0]}' got an unexpected number "
                    + f"of arguments (expected {option.nargs} but "
                    + f"got {len(values)})",
                    file=sys.stderr,
                )
                sys.exit(1)

    def _parse_preprocess_arguments(
        self, unprocessed: Iterable[Option | str]
    ) -> None:
        """
        Pre-processing arguments consists of
        * validating unexpected remaining Options
        """

        # handle bad order of options
        for arg in unprocessed:
            # validate strict options
            if isinstance(arg, Option):
                print(
                    f"Bad order, got option '{arg.names[0]}' in argument-"
                    + "section (use -- separator)",
                    file=sys.stderr,
                )
                sys.exit(1)

    def _parse_postprocess_arguments(
        self, unprocessed: Iterable[Option | str]
    ) -> None:
        """
        Post-processing arguments consists of
        * validating extra-arguments
        """
        if len(unprocessed) > 0:
            print(
                f"Command '{self.name}' got {len(unprocessed)} extra-"
                + "argument(s)",
                file=sys.stderr,
            )
            sys.exit(1)

    def _parse(self, raw: Iterable[str]) -> dict[str, list[Any]]:
        """Parse given raw input."""

        preprocessed = self._parse_preprocess_options(raw)

        if self.__help_option in preprocessed:
            self._print_help()

        # collect arguments by option
        result = {}
        unprocessed = list(reversed(preprocessed))
        while len(unprocessed) > 0:
            arg = unprocessed[-1]

            # check if option
            if isinstance(arg, Option):
                unprocessed.pop()
                option = arg
                option_name = option.names[0]
                # initialize collection
                if option_name not in result:
                    result[option_name] = []
            else:
                # options exhausted
                break

            # collect values for that option
            while len(unprocessed) > 0 and (
                len(result[option_name]) < option.nargs
            ):
                value = unprocessed[-1]
                if isinstance(value, Option) or value == "--":
                    # next option
                    break
                result[option_name].append(option.parse(value))
                unprocessed.pop()

        self._parse_postprocess_options(result)

        self._parse_preprocess_arguments(unprocessed)

        # remove separator if needed
        if len(unprocessed) > 0 and unprocessed[-1] == "--":
            unprocessed.pop()

        # process arguments
        for argument in self.__arguments_list:

            result[argument.name] = []
            if argument.nargs < 0:
                result[argument.name].extend(map(argument.parse, unprocessed))
                unprocessed.clear()
            else:
                for _ in range(argument.nargs):
                    if len(unprocessed) == 0:
                        print(
                            f"Argument '{argument.name}' got too few values "
                            + f"(expected {argument.nargs} but got "
                            + f"{len(result[argument.name])})",
                            file=sys.stderr,
                        )
                        sys.exit(1)
                    result[argument.name].append(
                        argument.parse(unprocessed.pop())
                    )

        self._parse_postprocess_arguments(unprocessed)

        return result

    def _print_help(self):
        """Prints help to stdout then exit."""

        def break_into_indented_lines(
            text: Optional[str],
            indent: int,
            relative_indent: int,
            width: int,
        ) -> list[str]:
            """Returns broken down text."""
            if text is None:
                return []
            result = []
            remainder = text
            line = ""
            while True:
                if remainder.strip() == "":
                    if line != "":
                        result.append(line)
                    break

                # initialize line
                if line.strip() == "":
                    line = " " * (indent + relative_indent * (len(result) > 0))

                # get next word
                try:
                    word, remainder = remainder.split(maxsplit=1)
                except ValueError:
                    word = remainder.strip()
                    remainder = ""

                # determine mode of operation
                if len(line) + len(word) + 1 > width:
                    if len(line.strip()) > 0:
                        # try in next line
                        remainder = word + " " + remainder
                    else:
                        remainder = (
                            word[width - 1 - len(line) :] + " " + remainder
                        )
                        line += (
                            " " * (len(line.strip()) > 0)
                            + word[: width - 1 - len(line)]
                        )
                    result.append(line)
                    line = ""
                    continue

                line += " " * (len(line.strip()) > 0) + word

            return result

        try:
            w, _ = os.get_terminal_size()
        except OSError:
            w = 100
        w = max(w, 41) - 3
        lines = break_into_indented_lines(self.helptext, 0, 0, w)
        indent = 2
        space = 1

        if len(lines) > 0:
            lines += [""]

        lines += break_into_indented_lines(
            "Usage: [command] [subcommand] [options] [--] [args]", 0, indent, w
        )

        for category, records in [
            (
                "Subcommands:",
                [
                    (command[0].name, command[0])
                    for command in self.__subcommands.values()
                ],
            ),
            (
                "Options:",
                [
                    (", ".join(sorted(option.names, key=len)), option)
                    for option in set(self.__options_map.values())
                ],
            ),
            (
                "Arguments:",
                [
                    (
                        argument.name
                        + (
                            ""
                            if argument.nargs == 1
                            else f" [1..{'n' if argument.nargs < 0 else argument.nargs}]"
                        ),
                        argument,
                    )
                    for argument in self.__arguments_list
                ],
            ),
        ]:
            if len(records) > 0:
                lines += ["", category]
                for record_name, record in sorted(records, key=lambda o: o[0]):
                    w_left = min(round(w / 2), 35) - indent
                    w_right = w - min(round(w / 2), 35) - space
                    record_left = break_into_indented_lines(
                        record_name,
                        indent,
                        indent,
                        w_left,
                    )
                    record_right = break_into_indented_lines(
                        record.helptext or "- no description provided -",
                        indent,
                        indent,
                        w_right,
                    )
                    for left, right in zip_longest(
                        record_left, record_right, fillvalue=""
                    ):
                        lines += [
                            left + " " * (space + w_left - len(left)) + right
                        ]

        print("\n".join(lines))
        sys.exit(0)

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
        def command(raw: Optional[Iterable[str]] = None) -> None:
            # load raw input
            if raw is None:
                raw = sys.argv[1:]

            # determine subcommand
            if len(raw) > 0 and raw[0] in self.__subcommands:
                self.__subcommands[raw[0]][1](raw[1:])

            # parse
            args = self._parse(raw)

            # help
            if help_ and ("-h" in args or "--help" in args):
                self._print_help()

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
        args: dict[str, list[Any]],
    ) -> tuple[bool, Optional[str]]:
        """Post-parse validation of input"""
        return True, None

    @abstractmethod
    def run(self, args: dict[str, list[Any]]) -> None:
        """`Command`'s business logic."""
        raise NotImplementedError("")


Cli = Command
