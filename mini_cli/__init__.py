from .parser import Parsers
from .argument import Argument
from .option import Option
from .command import Command, Cli


class MySubCommand(Command):
    args = Argument("args", nargs=-1)

    def run(self, args):
        print(args)


class MyCli(Cli):
    cmd1 = MySubCommand("subcmd")

    do = Option(
        ("-d", "--do"),
        helptext="file to do on",
        nargs=1,
        parser=Parsers.parse_file,
    )
    what = Option(
        ("-w", "--what"),
        helptext="whether to what as well",
        nargs=0,
    )
    when = Option(
        ("--when",),
        helptext="when to do",
        nargs=1,
    )

    arg0 = Argument(
        "arg0", helptext="..", parser=Parsers.parse_file, position=0
    )
    arg1 = Argument("arg1", helptext="...", position=1)

    def validate(self, args):
        if "what" in args and "do" not in args:
            return False, "Cannot run what without do."
        return True, None

    def run(self, args):
        print(args)


my_cli = MyCli("demo").build(src=..., completion=True, help=True, helptext="")
