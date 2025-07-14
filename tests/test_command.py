"""Test module for `command.py`."""

import pytest

from befehl import Argument, Option, Command


class _TestCommand(Command):
    def run(self, args):
        return


class TestCommandBuild:
    """Test `Command.build`."""
    def test_command_build_options_uniqueness(self):
        """Test `Command.build` option uniqueness."""

        with pytest.raises(ValueError) as exc_info:
            class _(_TestCommand):
                o1 = Option("--test")
                o2 = Option("--test")

            _("test").build()
        print(exc_info.value)

        with pytest.raises(ValueError) as exc_info:
            class _(_TestCommand):
                o1 = Option(("-t", "--test"))
                o2 = Option("--test")

            _("test").build()
        print(exc_info.value)

    def test_command_build_options_whitespace(self):
        """Test `Command.build` option whitespace."""

        with pytest.raises(ValueError) as exc_info:
            class _(_TestCommand):
                o1 = Option("--t est")

            _("test").build()
        print(exc_info.value)

        with pytest.raises(ValueError) as exc_info:
            class _(_TestCommand):
                o1 = Option("--t\nest")

            _("test").build()
        print(exc_info.value)

        with pytest.raises(ValueError) as exc_info:
            class _(_TestCommand):
                o1 = Option("--t\test")

            _("test").build()
        print(exc_info.value)

    def test_command_build_options_startswith(self):
        """Test `Command.build` option startswith."""

        with pytest.raises(ValueError) as exc_info:
            class _(_TestCommand):
                o1 = Option("test")

            _("test").build()
        print(exc_info.value)

    def test_command_build_options_separator(self):
        """Test `Command.build` option separator."""

        with pytest.raises(ValueError) as exc_info:
            class _(_TestCommand):
                o1 = Option("--")

            _("test").build()
        print(exc_info.value)

        class _(_TestCommand):
            o1 = Option("--x")

        _("test").build()

    def test_command_build_options_bad_characters(self):
        """Test `Command.build` option bad characters."""

        with pytest.raises(ValueError) as exc_info:
            class _(_TestCommand):
                o1 = Option("--test=bad")

            _("test").build()
        print(exc_info.value)

    def test_command_build_options_missing_characters(self):
        """Test `Command.build` option missing characters."""

        with pytest.raises(ValueError) as exc_info:
            class _(_TestCommand):
                o1 = Option("-")

            _("test").build()
        print(exc_info.value)

    def test_command_build_options_short_long(self):
        """Test `Command.build` option short long."""

        with pytest.raises(ValueError) as exc_info:
            class _(_TestCommand):
                o1 = Option(("-test"))

            _("test").build()
        print(exc_info.value)

        class _(_TestCommand):
            o1 = Option(("-t", "--test"))

        _("test").build()

    def test_command_build_subcommand_ambiguous(self):
        """Test `Command.build` subcommand ambiguous."""

        with pytest.raises(ValueError) as exc_info:
            class _(_TestCommand):
                c1 = _TestCommand("test")
                c2 = _TestCommand("test")

            _("test").build()
        print(exc_info.value)

        class _(_TestCommand):
            c1 = _TestCommand("test1")
            c2 = _TestCommand("test2")

        _("test").build()

    def test_command_build_subcommand_whitespace(self):
        """Test `Command.build` subcommand whitespace."""

        with pytest.raises(ValueError) as exc_info:
            class _(_TestCommand):
                c = _TestCommand("te st")

            _("test").build()
        print(exc_info.value)

        with pytest.raises(ValueError) as exc_info:
            class _(_TestCommand):
                c = _TestCommand("te\nst")

            _("test").build()
        print(exc_info.value)

        with pytest.raises(ValueError) as exc_info:
            class _(_TestCommand):
                c = _TestCommand("te\tst")

            _("test").build()
        print(exc_info.value)

    def test_command_build_subcommand_leading_character(self):
        """Test `Command.build` subcommand leading character."""

        with pytest.raises(ValueError) as exc_info:
            class _(_TestCommand):
                c = _TestCommand("-test")

            _("test").build()
        print(exc_info.value)

    def test_command_build_argument_infinite_nargs(self):
        """Test `Command.build` argument infinite nargs."""

        with pytest.raises(ValueError) as exc_info:
            class _(_TestCommand):
                a0 = Argument("a0", nargs=-1)
                a1 = Argument("a1")

            _("test").build()
        print(exc_info.value)

    def test_command_build_argument_position_all_or_none(self):
        """Test `Command.build` argument position all or none."""

        with pytest.raises(ValueError) as exc_info:
            class _(_TestCommand):
                a0 = Argument("a0", position=-1)
                a1 = Argument("a1")

            _("test").build()
        print(exc_info.value)

        class _(_TestCommand):
            a0 = Argument("a0", position=-1)
            a1 = Argument("a1", position=1)

        _("test").build()

        class _(_TestCommand):
            a0 = Argument("a0")
            a1 = Argument("a1")

        _("test").build()

    def test_command_build_argument_position_duplicate(self):
        """Test `Command.build` argument position duplicate."""

        with pytest.raises(ValueError) as exc_info:
            class _(_TestCommand):
                a0 = Argument("a0", position=1)
                a1 = Argument("a1", position=1)

            _("test").build()
        print(exc_info.value)

    def test_command_build_help(self):
        """Test `Command.build` option conflicting with help."""

        with pytest.raises(ValueError) as exc_info:
            class _(_TestCommand):
                o = Option("-h")

            _("test").build()
        print(exc_info.value)

        with pytest.raises(ValueError) as exc_info:
            class _(_TestCommand):
                o = Option("--help")

            _("test").build()
        print(exc_info.value)

        class _(_TestCommand):
            o = Option("--help")

        _("test").build(help_=False)

    def test_command_build_completion(self):
        """Test `Command.build` option conflicting with completion."""

        with pytest.raises(ValueError) as exc_info:
            class _(_TestCommand):
                o = Option("--generate-autocomplete")

            _("test").build(completion=True)
        print(exc_info.value)

        class _(_TestCommand):
            o = Option("--generate-autocomplete")

        _("test").build()


class TestCommandRun:
    """Test running `Command`."""

    class MirrorCommand(Command):
        """
        Stub for Command that mirrors input into class attribute on
        call.
        """
        def __init__(self, *args, **kwargs):
            self.mirror = {}
            self.ran = False
            super().__init__(*args, **kwargs)

        def run(self, args):
            self.ran = True
            self.mirror.clear()
            self.mirror.update(args)

    def test_command_run_minimal(self):
        """Test running `Command` minimal."""

        class Cli(self.MirrorCommand):
            pass

        base_cmd = Cli("test")
        cli = base_cmd.build()
        cli([])
        assert base_cmd.ran
        assert not base_cmd.mirror

    def test_command_run_validation(self):
        """Test running `Command` validation."""

        class Cli(self.MirrorCommand):
            def validate(self, args):
                return False, "Not valid"

        base_cmd = Cli("test")
        cli = base_cmd.build()
        with pytest.raises(SystemExit):
            cli([])
        assert not base_cmd.ran

    def test_command_run_subcommand(self):
        """Test running `Command` subcommand."""

        class Cli(self.MirrorCommand):
            com = self.MirrorCommand("subcommand")

        base_cmd = Cli("test")
        cli = base_cmd.build()
        cli(["subcommand"])
        assert not base_cmd.ran
        assert Cli.com.ran
        assert not Cli.com.mirror

    def test_command_run_unused_subcommand(self):
        """Test running `Command` unused subcommand."""

        class Cli(self.MirrorCommand):
            com = self.MirrorCommand("subcommand")

        base_cmd = Cli("test")
        cli = base_cmd.build()
        cli([])
        assert base_cmd.ran
        assert not Cli.com.ran

    def test_command_run_option(self):
        """Test running `Command` option."""

        class Cli(self.MirrorCommand):
            opt = Option(("-o", "--option"), nargs=1)

        base_cmd = Cli("test")
        cli = base_cmd.build()
        cli(["-o", "value"])
        assert base_cmd.ran
        assert base_cmd.mirror == {Cli.opt: ["value"]}

    def test_command_run_option_parser(self):
        """Test running `Command` option."""

        class Cli(self.MirrorCommand):
            opt = Option(
                ("-o", "--option"),
                nargs=1,
                parser=lambda s: (True, None, s[::-1]),
            )

        base_cmd = Cli("test")
        cli = base_cmd.build()
        cli(["-o", "value"])
        assert base_cmd.ran
        assert base_cmd.mirror == {Cli.opt: ["eulav"]}

    def test_command_run_option_parser_bad(self):
        """Test running `Command` option."""

        class Cli(self.MirrorCommand):
            opt = Option(
                ("-o", "--option"),
                nargs=1,
                parser=lambda s: (False, "bad parser", None),
            )

        base_cmd = Cli("test")
        cli = base_cmd.build()
        with pytest.raises(SystemExit):
            cli(["-o", "value"])
        assert not base_cmd.ran

    def test_command_run_option_unknown(self):
        """Test running `Command` option unknown."""

        class Cli(self.MirrorCommand):
            opt = Option(("-o", "--option"), nargs=0)

        base_cmd = Cli("test")
        cli = base_cmd.build()
        with pytest.raises(SystemExit):
            cli(["-a"])
        assert not base_cmd.ran

    def test_command_run_option_equal(self):
        """Test running `Command` option with value containing '='."""

        class Cli(self.MirrorCommand):
            opt = Option(("-o", "--option"), nargs=1)

        base_cmd = Cli("test")
        cli = base_cmd.build()
        with pytest.raises(SystemExit):
            cli(["-o", "-value"])
        with pytest.raises(SystemExit):
            cli(["-o", "--value"])
        assert not base_cmd.ran
        cli(["-o=-value"])
        assert base_cmd.ran
        assert base_cmd.mirror == {Cli.opt: ["-value"]}
        base_cmd.ran = False
        cli(["-o=--value"])
        assert base_cmd.ran
        assert base_cmd.mirror == {Cli.opt: ["--value"]}

    def test_command_run_option_groups(self):
        """Test running `Command` option groups."""

        class Cli(self.MirrorCommand):
            opt = Option(("-o", "--option"), nargs=0)
            opt2 = Option(("-p", "--option2"), nargs=0)

        base_cmd = Cli("test")
        cli = base_cmd.build()
        with pytest.raises(SystemExit):
            cli(["-opa"])
        assert not base_cmd.ran
        cli(["-op"])
        assert base_cmd.ran
        assert base_cmd.opt in base_cmd.mirror
        assert base_cmd.opt2 in base_cmd.mirror

    def test_command_run_option_missing_extra(self):
        """Test running `Command` option missing/extra."""

        class Cli(self.MirrorCommand):
            opt = Option(("-o", "--option"), nargs=1)

        base_cmd = Cli("test")
        cli = base_cmd.build()
        with pytest.raises(SystemExit):
            cli(["-o"])
        assert not base_cmd.ran
        with pytest.raises(SystemExit):
            cli(["-o", "0", "1"])
        assert not base_cmd.ran
        cli(["-o", "0"])
        assert base_cmd.ran

    def test_command_run_option_missing_not_strict(self):
        """Test running `Command` option missing not strict."""

        class Cli(self.MirrorCommand):
            opt = Option(("-o", "--option"), nargs=1, strict=False)

        base_cmd = Cli("test")
        cli = base_cmd.build()
        cli(["-o"])
        assert base_cmd.ran
        base_cmd.ran = False
        cli(["-o", "0"])
        assert base_cmd.ran
        base_cmd.ran = False
        with pytest.raises(SystemExit):
            cli(["-o", "0", "1"])
        assert not base_cmd.ran

    def test_command_run_argument(self):
        """Test running `Command` argument."""

        class Cli(self.MirrorCommand):
            arg = Argument("arg")

        base_cmd = Cli("test")
        cli = base_cmd.build()
        with pytest.raises(SystemExit):
            cli([])
        assert not base_cmd.ran
        with pytest.raises(SystemExit):
            cli(["a", "b"])
        assert not base_cmd.ran
        cli(["a"])
        assert base_cmd.ran
        assert Cli.arg in base_cmd.mirror
        assert base_cmd.mirror[Cli.arg] == ["a"]

    def test_command_run_argument_infinite(self):
        """Test running `Command` argument infinite."""

        class Cli(self.MirrorCommand):
            arg = Argument("arg", nargs=-1)

        base_cmd = Cli("test")
        cli = base_cmd.build()
        cli([])
        assert base_cmd.ran
        assert len(base_cmd.mirror.get(Cli.arg, [])) == 0
        base_cmd.ran = False
        cli(["a"])
        assert base_cmd.ran
        assert len(base_cmd.mirror.get(Cli.arg, [])) == 1
        base_cmd.ran = False
        cli(["a", "b"])
        assert base_cmd.ran
        assert len(base_cmd.mirror.get(Cli.arg, [])) == 2

    def test_command_run_argument_unexpected_option(self):
        """Test running `Command` argument."""

        class Cli(self.MirrorCommand):
            opt = Option("-o", nargs=0)
            arg = Argument("arg", nargs=-1)

        base_cmd = Cli("test")
        cli = base_cmd.build()
        with pytest.raises(SystemExit):
            cli(["-o", "a", "-o"])
        assert not base_cmd.ran
        cli(["-o", "--", "a", "-o"])
        assert base_cmd.ran
        assert Cli.opt in base_cmd.mirror
        assert sorted(base_cmd.mirror[Cli.opt]) == []
        assert Cli.arg in base_cmd.mirror
        assert sorted(base_cmd.mirror[Cli.arg]) == ["-o", "a"]

    def test_command_run_subcommand_w_opt_and_arg(self):
        """Test running `Command` more complex subcommand."""

        class Subcommand(self.MirrorCommand):
            opt = Option(("-o", "--sub-option"), nargs=1)
            arg = Argument("sub_arg", nargs=-1)

        class Cli(self.MirrorCommand):
            com = Subcommand("subcommand")

        base_cmd = Cli("test")
        cli = base_cmd.build()
        cli(["subcommand", "-o", "a", "0", "1"])
        assert Cli.com.ran
        assert base_cmd.mirror == {}
        assert Cli.com.arg in Cli.com.mirror
        assert sorted(Cli.com.mirror[Cli.com.arg]) == ["0", "1"]
        assert Cli.com.opt in Cli.com.mirror
        assert Cli.com.mirror[Cli.com.opt] == ["a"]

    def test_command_run_subcommand_help_autocomplete(self):
        """Test running `Command` help and autocomplete."""

        class Subcommand(self.MirrorCommand):
            opt = Option(("-o", "--sub-option"))
            arg = Argument("sub_arg", nargs=-1)

        class Cli(self.MirrorCommand):
            com = Subcommand("subcommand")
            opt = Option(("-o", "--option"))
            arg = Argument("arg")

        base_cmd = Cli("test", helptext="Test-cli")
        cli = base_cmd.build(completion=True)
        with pytest.raises(SystemExit):
            cli(["-h"])
        with pytest.raises(SystemExit):
            cli(["subcommand", "-h"])
        with pytest.raises(SystemExit):
            cli(["--generate-autocomplete"])
