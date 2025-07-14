 ![Tests](https://github.com/RichtersFinger/befehl/actions/workflows/tests.yml/badge.svg?branch=main) ![PyPI - License](https://img.shields.io/pypi/l/befehl) ![GitHub top language](https://img.shields.io/github/languages/top/RichtersFinger/befehl) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/befehl) ![PyPI version](https://badge.fury.io/py/befehl.svg) ![PyPI - Wheel](https://img.shields.io/pypi/wheel/befehl)

# befehl
`befehl` (german for `command`) is a
* declarative
* modular (easily reuse definitions),
* lightweight (no external dependencies), and
* versatile (highly customizable behavior through custom parsers and validation)

python library for building CLI applications.

It features
* a modern, declarative API,
* QoL features like short-option grouping,
* automatic generation of help-options, and
* generation of bash-autocomplete source files.

## Example

```python
from befehl import Parser, Option, Argument, Command, Cli

# define subcommand
class MySubCommand(Command):
    opt = Option("--sub-option")
    arg = Argument("subarg", nargs=-1)

    def run(self, args):
        # run business logic on parsed input
        # ...

    def validate(self, args):
        # perform custom validation on parsed input
        # ...

# define base-command
class MyCli(Cli):
    cmd = MySubCommand("subcommand")

    opt0 = Option(("-o", "--option-zero"))
    opt1 = Option(("-p", "--option-one"))

    arg0 = Argument("arg", parser=Parser.parse_as_path)

    def run(self, args):
        # run business logic on parsed input
        # ...

    def validate(self, args):
        # perform custom validation on parsed input
        # ...

# validate + build entry-point
cli = MyCli("my-cli").build()
```

## Documentation
### Command declaration
One of the few limitation imposed by this library is that all CLIs have the following structure:
```
[command] [subcommand1 [subcommand 2 [...]]] [options] [--] [arguments]
```

When defining a CLI, the command-tree is built from classes inheriting from `Command`.
A `Command`-class encapsulates all (immediate) subcommands (i.e., instances of previously defined `Commands`), `Options`, and `Arguments` as class attributes:
```python
class MySubCommand(Command):
    ...

class MyCli(Cli):
    cmd = MySubCommand("subcommand")

    opt0 = Option(("-o", "--option-zero"))
    opt1 = Option(("-p", "--option-one"))

    arg0 = Argument("arg", parser=Parser.parse_as_path)

    ...
```
(`Cli` is an optional alias for `Command`)

### Business logic

A `Command`'s business logic is defined in its `run` method, e.g.,
```python
class MyCli(Cli):
    ...

    def run(self, args):
        print(args)
```

When being executed, this function receives a singular argument `args: dict[Option | Argument, list[Any]]`, where values are lists of parsed values.

For example, invoking the `Command` from above with a call like
```
command -o path/to/file
```
results in an `args`-mapping of
```python
args = {
    MyCli.opt0: [],
    MyCli.arg0: [Path(path/to/file)]
}
```
Multiple values to a single `Option` or `Argument` keep their order in the generated list.

### Validation

Optionally, before entering the business-logic, a validation-step can be defined.
To this end, the empty `validate` method of the `Command` class can be overwritten.
For example, the following definition validates that, if `-o` is given, option `-p` is needed as well.
```python
class MyCli(Cli):
    ...

    def validate(self, args):
        if self.opt0 in args and self.opt1 not in args:
            return (
                False,
                f"option {self.opt0} also requires option {self.opt1}"
            )
        return True, None
```

Invoking the cli with `command -o` returns with the above message (and exit code 1) whereas `command -op` continues past the validation into the `run`-method.

### Build

In order to create a callable function that can be used as an entry-point for python packages, a build-step has to be performed.

For example, for the above CLI, one can enter
```python
...

cli = MyCli("my-cli").build(help_=True, completion=False)
```
The variable `cli` then serves as the entry-point.
Suppose, this variable is in the namespace of the module `cli`, then it can be used with, for example, `setuptools` as
```python
setup(
    ...
    entry_points={
        "console_scripts": [
            "command = cli:cli",
        ],
    },
    ...
)
```

When building, it has to be decided, whether
* a help-option (`-h, --help`) should be generated (enabled by default)
* an option (`--generate-autocomplete`) for generating a sourcable bash-autocomplete script should be added (disabled by default; enabled if environment sets `_BEFEHL_COMPLETION`). See [this section](#autocomplete) for details.

### Parsers

Both `Option`s and `Argument`s accept keyword arguments for a `parser`.
A `parser` is a function that accepts a single string-value and returns a tuple of
* boolean (whether input is valid),
* string (message in case the input is invalid), and
* any object (parsed data in case of success).

This library provides some basic parsers to be used in `Option`s and `Argument`s.
These range from parsing of primitive types like boolean or integer to more involved parsers for paths/files/directories (using `pathlib.Path`) or requiring values to satisfy regular expressions.

Pre-defined parsers are accessible via the abstract collection class `Parser` and can be accessed via its static methods like
```python
class AnotherCommand(Command):
    opt = Option("-o", parser=Parser.parse_as_int)
    arg = Argument("arg", parser=Parser.parse_with_regex(r"[0-9]+"))

    ...
```

Lastly, by using the methods `Parser.first` or `Parser.chain`, multiple parsers can be applied to single values.

## Other features
### (Short) Option grouping
This library supports `Option`s in short and long format:
* short corresponds to starting with single `-` followed by a single character
* long `Option`s start with `--` followed by at least one character

For convenience, `Option`s with short name and `nargs=0` can be grouped.
For example, when using the `Command` from above, the two inputs
```
command -o -p
```
and
```
command -op
```
are equivalent.

### Equal-sign syntax
In order to avoid problems with `Option` values starting with `-` (could be ambiguous regarding other `Option`s), `Option`s can be used with the following syntax
```
command --delta=-1
```
(instead of `command --delta -1` which would fail).

### Separator for options and arguments
Similar to the problem described in the [previous section](#equal-sign-syntax): In order to avoid problems with `Argument` values starting with `-` (could be ambiguous regarding `Option`s), the separator `--` can be used like
```
command -o -- -1
```
(instead of `command -o -1` which would fail).

### Autocomplete
This library can generate shell-script files that, when sourced in bash, enable basic autocomplete functionality.
The script can be built by first setting the `completion`-option during [build](#build) and then call the CLI with the `--generate-autocomplete` option (will be printed to stdout).

The auto-completion can also be sourced immediately by entering
```
eval "$(_BEFEHL_COMPLETION= <entry-point> --generate-autocomplete)"
```
(replace `<entry-point>` with your custom entry-point).

## Tests

Automated (`pytest`-)tests can be run by first installing this package as well as its dev-dependencies via
```
pip install .
pip install -r dev-requirements.txt
```
Afterwards, simply enter
```
pytest
```
