"""
Python `befehl`.

Example usage:

    ```
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

The callable `cli` can then be used as entry-point.

See project README at `https://github.com/RichtersFinger/befehl` for
details.
"""


from .parser import Parser
from .argument import Argument
from .option import Option
from .command import Command, Cli


__all__ = [
    "Parser", "Argument", "Option", "Command", "Cli",
]
