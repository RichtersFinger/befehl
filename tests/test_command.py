"""Test module for `command.py`."""

import pytest

from mini_cli import Argument, Option, Command


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
