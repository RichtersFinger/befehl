"""Test module for `parser.py`."""

from pathlib import Path
from unittest import TestCase

from befehl import Parser


class TestParser(TestCase):
    """Test `Parser`."""

    def test_boolean(self):
        """Test `parse_as_bool`."""
        with self.subTest(case="invalid"):
            ok, msg, data = Parser.parse_as_bool("a")
            self.assertFalse(ok)
            print(msg)

        with self.subTest(case="valid"):
            ok, msg, data = Parser.parse_as_bool("y")
            self.assertTrue(ok)
            self.assertIs(data, True)

    def test_int(self):
        """Test `parse_as_int`."""
        with self.subTest(case="invalid"):
            ok, msg, data = Parser.parse_as_int("a")
            self.assertFalse(ok)
            print(msg)

        with self.subTest(case="valid"):
            ok, msg, data = Parser.parse_as_int("1")
            self.assertTrue(ok)
            self.assertEqual(data, 1)

    def test_float(self):
        """Test `parse_as_float`."""
        with self.subTest(case="invalid"):
            ok, msg, data = Parser.parse_as_float("a")
            self.assertFalse(ok)
            print(msg)

        with self.subTest(case="valid"):
            ok, msg, data = Parser.parse_as_float("1.5")
            self.assertTrue(ok)
            self.assertEqual(data, 1.5)

    def test_path(self):
        """Test `parse_as_path`."""
        with self.subTest(case="invalid"):
            ok, msg, data = Parser.parse_as_path("a")
            self.assertFalse(ok)
            print(msg)

        with self.subTest(case="valid"):
            ok, msg, data = Parser.parse_as_path("tests")
            self.assertTrue(ok)
            self.assertEqual(data, Path("tests"))

    def test_dir(self):
        """Test `parse_as_dir`."""
        with self.subTest(case="invalid"):
            ok, msg, data = Parser.parse_as_dir("a")
            self.assertFalse(ok)
            print(msg)

        with self.subTest(case="file instead of dir"):
            ok, msg, data = Parser.parse_as_dir("tests/test_parser.py")
            self.assertFalse(ok)
            print(msg)

        with self.subTest(case="valid"):
            ok, msg, data = Parser.parse_as_dir("tests")
            self.assertTrue(ok)
            self.assertEqual(data, Path("tests"))

    def test_file(self):
        """Test `parse_as_file`."""
        with self.subTest(case="invalid"):
            ok, msg, data = Parser.parse_as_file("a")
            self.assertFalse(ok)
            print(msg)

        with self.subTest(case="dir instead of file"):
            ok, msg, data = Parser.parse_as_file("tests")
            self.assertFalse(ok)
            print(msg)

        with self.subTest(case="valid"):
            ok, msg, data = Parser.parse_as_file("tests/test_parser.py")
            self.assertTrue(ok)
            self.assertEqual(data, Path("tests/test_parser.py"))

    def test_values(self):
        """Test `parse_with_values`."""
        with self.subTest(case="invalid"):
            ok, msg, data = Parser.parse_with_values(["a", "b"])("c")
            self.assertFalse(ok)
            print(msg)

        with self.subTest(case="valid"):
            ok, msg, data = Parser.parse_with_values(["a", "b"])("a")
            self.assertTrue(ok)
            self.assertEqual(data, "a")

    def test_glob(self):
        """Test `parse_with_glob`."""
        with self.subTest(case="invalid"):
            ok, msg, data = Parser.parse_with_glob("c/*")("a/b")
            self.assertFalse(ok)
            print(msg)

        with self.subTest(case="valid"):
            ok, msg, data = Parser.parse_with_glob("c/*")("c/d")
            self.assertTrue(ok)
            self.assertEqual(data, Path("c/d"))

    def test_regex(self):
        """Test `parse_with_regex`."""
        with self.subTest(case="invalid"):
            ok, msg, data = Parser.parse_with_regex("[0-9]*")("a")
            self.assertFalse(ok)
            print(msg)

        with self.subTest(case="valid"):
            ok, msg, data = Parser.parse_with_regex("[0-9]*")("0")
            self.assertTrue(ok)
            self.assertEqual(data, "0")

    def test_first(self):
        """Test `first`."""
        with self.subTest(case="first succeeds"):
            ok, msg, data = Parser.first(
                Parser.parse_with_values(["a"]), Parser.parse_as_int
            )("a")
            self.assertTrue(ok)
            self.assertEqual(data, "a")

        with self.subTest(case="second succeeds"):
            ok, msg, data = Parser.first(
                Parser.parse_with_values(["a"]), Parser.parse_as_int
            )("1")
            self.assertTrue(ok)
            self.assertEqual(data, 1)

        with self.subTest(case="both fail"):
            ok, msg, data = Parser.first(
                Parser.parse_with_values(["a"]), Parser.parse_as_int
            )("b")
            self.assertFalse(ok)
            print(msg)

    def test_chain(self):
        """Test `chain`."""
        with self.subTest(case="first link fails"):
            ok, msg, data = Parser.chain(
                Parser.parse_with_regex("[a-z]*"),
                Parser.parse_with_regex("[0-9]*"),
            )("a0")
            self.assertFalse(ok)
            print(msg)

        with self.subTest(case="second link fails"):
            ok, msg, data = Parser.chain(
                Parser.parse_with_regex("[a-z]*"),
                Parser.parse_with_regex("[0-9]*"),
            )("0a")
            self.assertFalse(ok)
            print(msg)

        with self.subTest(case="both links succeed"):
            ok, msg, data = Parser.chain(
                Parser.parse_with_regex("[a-z]*[0-9]*"),
                Parser.parse_with_regex("[a-z]*[0-9]*"),
            )("a0")
            self.assertTrue(ok)
            self.assertEqual(data, "a0")

        with self.subTest(case="type casting chain"):
            ok, msg, data = Parser.chain(
                Parser.parse_as_float, Parser.parse_as_int
            )("1")
            self.assertTrue(ok)
            self.assertEqual(data, 1)
