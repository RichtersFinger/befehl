"""Test module for `command.py`."""

from unittest import TestCase

from befehl import Argument, Option, Command


class _TestCommand(Command):
    def run(self, args):
        return


class TestCommandBuild(TestCase):
    """Test `Command.build`."""

    def test_options_uniqueness(self):
        """Test option uniqueness."""
        with self.subTest(case="duplicate variable names"):
            with self.assertRaises(ValueError) as exc_info:

                class _(_TestCommand):
                    o1 = Option("--test")
                    o2 = Option("--test")

                _("test").build()
            print(exc_info.exception)

        with self.subTest(case="overlapping flags"):
            with self.assertRaises(ValueError) as exc_info:

                class _(_TestCommand):
                    o1 = Option(("-t", "--test"))
                    o2 = Option("--test")

                _("test").build()
            print(exc_info.exception)

    def test_options_whitespace(self):
        """Test option whitespace."""
        with self.subTest(case="space"):
            with self.assertRaises(ValueError) as exc_info:

                class _(_TestCommand):
                    o1 = Option("--t est")

                _("test").build()
            print(exc_info.exception)

        with self.subTest(case="newline"):
            with self.assertRaises(ValueError) as exc_info:

                class _(_TestCommand):
                    o1 = Option("--t\nest")

                _("test").build()
            print(exc_info.exception)

        with self.subTest(case="tab"):
            with self.assertRaises(ValueError) as exc_info:

                class _(_TestCommand):
                    o1 = Option("--t\test")

                _("test").build()
            print(exc_info.exception)

    def test_options_startswith(self):
        """Test option startswith."""
        with self.assertRaises(ValueError) as exc_info:

            class _(_TestCommand):
                o1 = Option("test")

            _("test").build()
        print(exc_info.exception)

    def test_options_separator(self):
        """Test option separator."""
        with self.subTest(case="bare separator invalid"):
            with self.assertRaises(ValueError) as exc_info:

                class _(_TestCommand):
                    o1 = Option("--")

                _("test").build()
            print(exc_info.exception)

        with self.subTest(case="valid separator"):

            class _(_TestCommand):
                o1 = Option("--x")

            _("test").build()

    def test_options_bad_characters(self):
        """Test option bad characters."""
        with self.assertRaises(ValueError) as exc_info:

            class _(_TestCommand):
                o1 = Option("--test=bad")

            _("test").build()
        print(exc_info.exception)

    def test_options_missing_characters(self):
        """Test option missing characters."""
        with self.assertRaises(ValueError) as exc_info:

            class _(_TestCommand):
                o1 = Option("-")

            _("test").build()
        print(exc_info.exception)

    def test_options_short_long(self):
        """Test option short long."""
        with self.subTest(case="single dash long name invalid"):
            with self.assertRaises(ValueError) as exc_info:

                class _(_TestCommand):
                    o1 = Option(("-test"))

                _("test").build()
            print(exc_info.exception)

        with self.subTest(case="valid short long combination"):

            class _(_TestCommand):
                o1 = Option(("-t", "--test"))

            _("test").build()

    def test_subcommand_ambiguous(self):
        """Test subcommand ambiguous."""
        with self.subTest(case="ambiguous names"):
            with self.assertRaises(ValueError) as exc_info:

                class _(_TestCommand):
                    c1 = _TestCommand("test")
                    c2 = _TestCommand("test")

                _("test").build()
            print(exc_info.exception)

        with self.subTest(case="distinct names"):

            class _(_TestCommand):
                c1 = _TestCommand("test1")
                c2 = _TestCommand("test2")

            _("test").build()

    def test_subcommand_whitespace(self):
        """Test subcommand whitespace."""
        with self.subTest(case="space"):
            with self.assertRaises(ValueError) as exc_info:

                class _(_TestCommand):
                    c = _TestCommand("te st")

                _("test").build()
            print(exc_info.exception)

        with self.subTest(case="newline"):
            with self.assertRaises(ValueError) as exc_info:

                class _(_TestCommand):
                    c = _TestCommand("te\nst")

                _("test").build()
            print(exc_info.exception)

        with self.subTest(case="tab"):
            with self.assertRaises(ValueError) as exc_info:

                class _(_TestCommand):
                    c = _TestCommand("te\tst")

                _("test").build()
            print(exc_info.exception)

    def test_subcommand_leading_character(self):
        """Test subcommand leading character."""
        with self.assertRaises(ValueError) as exc_info:

            class _(_TestCommand):
                c = _TestCommand("-test")

            _("test").build()
        print(exc_info.exception)

    def test_argument_infinite_nargs(self):
        """Test argument infinite nargs."""
        with self.assertRaises(ValueError) as exc_info:

            class _(_TestCommand):
                a0 = Argument("a0", nargs=-1)
                a1 = Argument("a1")

            _("test").build()
        print(exc_info.exception)

    def test_argument_position_all_or_none(self):
        """Test argument position all or none."""
        with self.subTest(case="mixed positions"):
            with self.assertRaises(ValueError) as exc_info:

                class _(_TestCommand):
                    a0 = Argument("a0", position=-1)
                    a1 = Argument("a1")

                _("test").build()
            print(exc_info.exception)

        with self.subTest(case="all positions set"):

            class _(_TestCommand):
                a0 = Argument("a0", position=-1)
                a1 = Argument("a1", position=1)

            _("test").build()

        with self.subTest(case="no positions set"):

            class _(_TestCommand):
                a0 = Argument("a0")
                a1 = Argument("a1")

            _("test").build()

    def test_argument_position_duplicate(self):
        """Test argument position duplicate."""
        with self.assertRaises(ValueError) as exc_info:

            class _(_TestCommand):
                a0 = Argument("a0", position=1)
                a1 = Argument("a1", position=1)

            _("test").build()
        print(exc_info.exception)

    def test_help(self):
        """Test option conflicting with help."""
        with self.subTest(case="conflicting short flag"):
            with self.assertRaises(ValueError) as exc_info:

                class _(_TestCommand):
                    o = Option("-h")

                _("test").build()
            print(exc_info.exception)

        with self.subTest(case="conflicting long flag"):
            with self.assertRaises(ValueError) as exc_info:

                class _(_TestCommand):
                    o = Option("--help")

                _("test").build()
            print(exc_info.exception)

        with self.subTest(case="disabled help"):

            class _(_TestCommand):
                o = Option("--help")

            _("test").build(help_=False)

    def test_completion(self):
        """Test option conflicting with completion."""
        with self.subTest(case="conflicting completion flag"):
            with self.assertRaises(ValueError) as exc_info:

                class _(_TestCommand):
                    o = Option("--generate-autocomplete")

                _("test").build(completion=True)
            print(exc_info.exception)

        with self.subTest(case="no completion flag"):

            class _(_TestCommand):
                o = Option("--generate-autocomplete")

            _("test").build()


class TestCommandRun(TestCase):
    """Test running `Command`."""

    class MirrorCommand(Command):
        """
        Stub for `Command` that mirrors input into class attribute on
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

    def test_minimal(self):
        """Test minimal."""

        class Cli(self.MirrorCommand):
            pass

        base_cmd = Cli("test")
        cli = base_cmd.build()
        cli([])
        self.assertTrue(base_cmd.ran)
        self.assertFalse(base_cmd.mirror)

    def test_validation(self):
        """Test validation."""

        class Cli(self.MirrorCommand):
            def validate(self, args):
                return False, "Not valid"

        base_cmd = Cli("test")
        cli = base_cmd.build()
        with self.assertRaises(SystemExit):
            cli([])
        self.assertFalse(base_cmd.ran)

    def test_subcommand(self):
        """Test subcommand."""

        class Cli(self.MirrorCommand):
            com = self.MirrorCommand("subcommand")

        base_cmd = Cli("test")
        cli = base_cmd.build()
        cli(["subcommand"])
        self.assertFalse(base_cmd.ran)
        self.assertTrue(Cli.com.ran)
        self.assertFalse(Cli.com.mirror)

    def test_unused_subcommand(self):
        """Test unused subcommand."""

        class Cli(self.MirrorCommand):
            com = self.MirrorCommand("subcommand")

        base_cmd = Cli("test")
        cli = base_cmd.build()
        cli([])
        self.assertTrue(base_cmd.ran)
        self.assertFalse(Cli.com.ran)

    def test_option(self):
        """Test option."""

        class Cli(self.MirrorCommand):
            opt = Option(("-o", "--option"), nargs=1)

        base_cmd = Cli("test")
        cli = base_cmd.build()
        cli(["-o", "value"])
        self.assertTrue(base_cmd.ran)
        self.assertDictEqual(base_cmd.mirror, {Cli.opt: ["value"]})

    def test_option_neg_nargs(self):
        """Test option with negative nargs."""

        class Cli(self.MirrorCommand):
            opt1 = Option(("-o", "--option"), nargs=-1)
            opt2 = Option(("-p", "--option-2"), nargs=-1)

        base_cmd = Cli("test")
        cli = base_cmd.build()
        cli(["-o", "value", "value2", "value3", "-p", "value4"])
        self.assertTrue(base_cmd.ran)
        self.assertDictEqual(
            base_cmd.mirror,
            {
                Cli.opt1: ["value", "value2", "value3"],
                Cli.opt2: ["value4"],
            },
        )

    def test_option_multiple_flags(self):
        """Test option multiple flags."""

        class Cli(self.MirrorCommand):
            opt = Option(("-o", "--option"), nargs=-1)

        base_cmd = Cli("test")
        cli = base_cmd.build()
        cli(["-o", "value", "-o", "value2"])
        self.assertTrue(base_cmd.ran)
        self.assertDictEqual(base_cmd.mirror, {Cli.opt: ["value", "value2"]})

    def test_option_parser(self):
        """Test option parser."""

        class Cli(self.MirrorCommand):
            opt = Option(
                ("-o", "--option"),
                nargs=1,
                parser=lambda s: (True, None, s[::-1]),
            )

        base_cmd = Cli("test")
        cli = base_cmd.build()
        cli(["-o", "value"])
        self.assertTrue(base_cmd.ran)
        self.assertDictEqual(base_cmd.mirror, {Cli.opt: ["eulav"]})

    def test_option_parser_bad(self):
        """Test option bad parser."""

        class Cli(self.MirrorCommand):
            opt = Option(
                ("-o", "--option"),
                nargs=1,
                parser=lambda s: (False, "bad parser", None),
            )

        base_cmd = Cli("test")
        cli = base_cmd.build()
        with self.assertRaises(SystemExit):
            cli(["-o", "value"])
        self.assertFalse(base_cmd.ran)

    def test_option_unknown(self):
        """Test option unknown."""

        class Cli(self.MirrorCommand):
            opt = Option(("-o", "--option"), nargs=0)

        base_cmd = Cli("test")
        cli = base_cmd.build()
        with self.assertRaises(SystemExit):
            cli(["-a"])
        self.assertFalse(base_cmd.ran)

    def test_option_equal(self):
        """Test option with value containing '='."""

        class Cli(self.MirrorCommand):
            opt = Option(("-o", "--option"), nargs=1)

        base_cmd = Cli("test")
        cli = base_cmd.build()

        with self.subTest(case="invalid start with dash short"):
            with self.assertRaises(SystemExit):
                cli(["-o", "-value"])
            self.assertFalse(base_cmd.ran)

        with self.subTest(case="invalid start with dash long"):
            with self.assertRaises(SystemExit):
                cli(["-o", "--value"])
            self.assertFalse(base_cmd.ran)

        with self.subTest(case="valid equal short format"):
            cli(["-o=-value"])
            self.assertTrue(base_cmd.ran)
            self.assertDictEqual(base_cmd.mirror, {Cli.opt: ["-value"]})

        with self.subTest(case="valid equal long format"):
            base_cmd.ran = False
            cli(["-o=--value"])
            self.assertTrue(base_cmd.ran)
            self.assertDictEqual(base_cmd.mirror, {Cli.opt: ["--value"]})

    def test_option_groups(self):
        """Test option groups."""

        class Cli(self.MirrorCommand):
            opt = Option(("-o", "--option"), nargs=0)
            opt2 = Option(("-p", "--option2"), nargs=0)

        base_cmd = Cli("test")
        cli = base_cmd.build()

        with self.subTest(case="unknown character in group"):
            with self.assertRaises(SystemExit):
                cli(["-opa"])
            self.assertFalse(base_cmd.ran)

        with self.subTest(case="valid group"):
            cli(["-op"])
            self.assertTrue(base_cmd.ran)
            self.assertIn(base_cmd.opt, base_cmd.mirror)
            self.assertIn(base_cmd.opt2, base_cmd.mirror)

    def test_option_missing_extra(self):
        """Test option missing/extra args."""

        class Cli(self.MirrorCommand):
            opt = Option(("-o", "--option"), nargs=1)

        base_cmd = Cli("test")
        cli = base_cmd.build()

        with self.subTest(case="missing arg"):
            with self.assertRaises(SystemExit):
                cli(["-o"])
            self.assertFalse(base_cmd.ran)

        with self.subTest(case="extra arg"):
            with self.assertRaises(SystemExit):
                cli(["-o", "0", "1"])
            self.assertFalse(base_cmd.ran)

        with self.subTest(case="exact arg"):
            cli(["-o", "0"])
            self.assertTrue(base_cmd.ran)

    def test_option_missing_not_strict(self):
        """Test option missing not strict."""

        class Cli(self.MirrorCommand):
            opt = Option(("-o", "--option"), nargs=1, strict=False)

        base_cmd = Cli("test")
        cli = base_cmd.build()

        with self.subTest(case="missing arg allowed"):
            cli(["-o"])
            self.assertTrue(base_cmd.ran)

        with self.subTest(case="exact arg allowed"):
            base_cmd.ran = False
            cli(["-o", "0"])
            self.assertTrue(base_cmd.ran)

        with self.subTest(case="extra arg strictly disallowed"):
            base_cmd.ran = False
            with self.assertRaises(SystemExit):
                cli(["-o", "0", "1"])
            self.assertFalse(base_cmd.ran)

    def test_argument(self):
        """Test argument."""

        class Cli(self.MirrorCommand):
            arg = Argument("arg")

        base_cmd = Cli("test")
        cli = base_cmd.build()

        with self.subTest(case="missing"):
            with self.assertRaises(SystemExit):
                cli([])
            self.assertFalse(base_cmd.ran)

        with self.subTest(case="extra"):
            with self.assertRaises(SystemExit):
                cli(["a", "b"])
            self.assertFalse(base_cmd.ran)

        with self.subTest(case="exact"):
            cli(["a"])
            self.assertTrue(base_cmd.ran)
            self.assertIn(Cli.arg, base_cmd.mirror)
            self.assertListEqual(base_cmd.mirror[Cli.arg], ["a"])

    def test_argument_infinite(self):
        """Test argument infinite."""

        class Cli(self.MirrorCommand):
            arg = Argument("arg", nargs=-1)

        base_cmd = Cli("test")
        cli = base_cmd.build()

        with self.subTest(case="zero args"):
            cli([])
            self.assertTrue(base_cmd.ran)
            self.assertEqual(len(base_cmd.mirror.get(Cli.arg, [])), 0)

        with self.subTest(case="one arg"):
            base_cmd.ran = False
            cli(["a"])
            self.assertTrue(base_cmd.ran)
            self.assertEqual(len(base_cmd.mirror.get(Cli.arg, [])), 1)

        with self.subTest(case="two args"):
            base_cmd.ran = False
            cli(["a", "b"])
            self.assertTrue(base_cmd.ran)
            self.assertEqual(len(base_cmd.mirror.get(Cli.arg, [])), 2)

    def test_argument_unexpected_option(self):
        """Test argument unexpected option."""

        class Cli(self.MirrorCommand):
            opt = Option("-o", nargs=0)
            arg = Argument("arg", nargs=-1)

        base_cmd = Cli("test")
        cli = base_cmd.build()

        with self.subTest(case="fails without double dash separator"):
            with self.assertRaises(SystemExit):
                cli(["-o", "a", "-o"])
            self.assertFalse(base_cmd.ran)

        with self.subTest(case="works with double dash separator"):
            cli(["-o", "--", "a", "-o"])
            self.assertTrue(base_cmd.ran)
            self.assertIn(Cli.opt, base_cmd.mirror)
            self.assertListEqual(sorted(base_cmd.mirror[Cli.opt]), [])
            self.assertIn(Cli.arg, base_cmd.mirror)
            self.assertListEqual(sorted(base_cmd.mirror[Cli.arg]), ["-o", "a"])

    def test_subcommand_w_opt_and_arg(self):
        """Test complex subcommand."""

        class Subcommand(self.MirrorCommand):
            opt = Option(("-o", "--sub-option"), nargs=1)
            arg = Argument("sub_arg", nargs=-1)

        class Cli(self.MirrorCommand):
            com = Subcommand("subcommand")

        base_cmd = Cli("test")
        cli = base_cmd.build()
        cli(["subcommand", "-o", "a", "0", "1"])
        self.assertTrue(Cli.com.ran)
        self.assertDictEqual(base_cmd.mirror, {})
        self.assertIn(Cli.com.arg, Cli.com.mirror)
        self.assertListEqual(sorted(Cli.com.mirror[Cli.com.arg]), ["0", "1"])
        self.assertIn(Cli.com.opt, Cli.com.mirror)
        self.assertListEqual(Cli.com.mirror[Cli.com.opt], ["a"])

    def test_subcommand_help_autocomplete(self):
        """Test help and autocomplete."""

        class Subcommand(self.MirrorCommand):
            opt = Option(("-o", "--sub-option"))
            arg = Argument("sub_arg", nargs=-1)

        class Cli(self.MirrorCommand):
            com = Subcommand("subcommand")
            opt = Option(("-o", "--option"))
            arg = Argument("arg")

        base_cmd = Cli("test", helptext="Test-cli")
        cli = base_cmd.build(completion=True)

        with self.subTest(case="base command help"):
            with self.assertRaises(SystemExit):
                cli(["-h"])

        with self.subTest(case="subcommand help"):
            with self.assertRaises(SystemExit):
                cli(["subcommand", "-h"])

        with self.subTest(case="autocomplete"):
            with self.assertRaises(SystemExit):
                cli(["--generate-autocomplete"])
