# mini-cli
A
* declarative
* modular (easily reuse definition)
* lightweight (no external dependencies), and
* versatile

python library for building cli applications.

## concept/initial thoughts

### description
* declarative w build-step (validation, cli-settings, entrypoint (cli and app))

### features
* automatic help
* enable to generate (bash) autocomplete source-file via cli command (if activated)
* short-option grouping (for shot/single-letter Options with nargs=0)

### misc
* run-args is a dict that is populated with user-input via parsers
  (uses custom keys for names if provided or otherwise attribute names)
* pre-defined parsers/parser-factories for:
  * values
  * regex
  * file/dir
  * number
  * ..
* fixed order "command [options] [arguments]"
* nargs=-1 for any number of args
* help-text output should adapt to shell size


### pre-viz
```python
from mini_cli import Command, Option, Argument


def parse_file(data) -> tuple[bool, Optional[str], Optional[Any]]:
    if Path(data).exists():
        return True, "", Path(data)
    return False, "Does not exist", None


class MySubCommand(Command):
    arg1 = Argument()

    def run(self, args):
        print(args)


class MyCli(Command):
    cmd1 = MySubCommand("subcmd")

    do = Option(
        "custom_name_for_do",
        names=("-d", "--do"),
        helptext="file to do on",
        nargs=1,
        parser=parse_file,
        repeatable=True,
    )
    what = Option(
        names=("-w", "--what"),
        helptext="whether to what as well",
        nargs=0,
    )
    when = Option(
        names=("--when"),
        helptext="when to do",
        nargs=1,
    )

    arg0 = Argument("other_file", helptext="..", parser=parse_file, position=0)
    args = Argument(helptext="...", nargs=-1, position=1)

    def validate(self, args):
        if "what" in args and "do" not in args:
            return False, "Cannot run what without do."
        return True, None

    def run(self, args):
        print(args)


my_cli = MyCli().build(
    src=lambda: sys.argv[1:], completion=True, help=True, helptext=""
)
```
