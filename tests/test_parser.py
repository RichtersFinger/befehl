"""Test module for `parser.py`."""

from pathlib import Path

from mini_cli import Parser


def test_boolean():
    """Test parser `Parser.parse_as_bool`."""
    ok, msg, data = Parser.parse_as_bool("a")
    assert not ok
    print(msg)

    ok, msg, data = Parser.parse_as_bool("y")
    assert ok
    assert data is True


def test_int():
    """Test parser `Parser.parse_as_int`."""
    ok, msg, data = Parser.parse_as_int("a")
    assert not ok
    print(msg)

    ok, msg, data = Parser.parse_as_int("1")
    assert ok
    assert data == 1


def test_float():
    """Test parser `Parser.parse_as_float`."""
    ok, msg, data = Parser.parse_as_float("a")
    assert not ok
    print(msg)

    ok, msg, data = Parser.parse_as_float("1.5")
    assert ok
    assert data == 1.5


def test_path():
    """Test parser `Parser.parse_as_path`."""
    ok, msg, data = Parser.parse_as_path("a")
    assert not ok
    print(msg)

    ok, msg, data = Parser.parse_as_path("tests")
    assert ok
    assert data == Path("tests")


def test_dir():
    """Test parser `Parser.parse_as_dir`."""
    ok, msg, data = Parser.parse_as_dir("a")
    assert not ok
    print(msg)

    ok, msg, data = Parser.parse_as_dir("tests/test_parser.py")
    assert not ok
    print(msg)

    ok, msg, data = Parser.parse_as_dir("tests")
    assert ok
    assert data == Path("tests")


def test_file():
    """Test parser `Parser.parse_as_file`."""
    ok, msg, data = Parser.parse_as_file("a")
    assert not ok
    print(msg)

    ok, msg, data = Parser.parse_as_file("tests")
    assert not ok
    print(msg)

    ok, msg, data = Parser.parse_as_file("tests/test_parser.py")
    assert ok
    assert data == Path("tests/test_parser.py")


def test_values():
    """Test parser `Parser.parse_with_glob`."""
    ok, msg, data = Parser.parse_with_values(["a", "b"])("c")
    assert not ok
    print(msg)

    ok, msg, data = Parser.parse_with_values(["a", "b"])("a")
    assert ok
    assert data == "a"


def test_glob():
    """Test parser `Parser.parse_with_glob`."""
    ok, msg, data = Parser.parse_with_glob("c/*")("a/b")
    assert not ok
    print(msg)

    ok, msg, data = Parser.parse_with_glob("c/*")("c/d")
    assert ok
    assert data == Path("c/d")


def test_regex():
    """Test parser `Parser.parse_with_glob`."""
    ok, msg, data = Parser.parse_with_regex("[0-9]*")("a")
    assert not ok
    print(msg)

    ok, msg, data = Parser.parse_with_regex("[0-9]*")("0")
    assert ok
    assert data == "0"


def test_chain():
    """Test parser `Parser.parse_with_glob`."""
    ok, msg, data = Parser.chain(
        Parser.parse_with_regex("[a-z]*"), Parser.parse_with_regex("[0-9]*")
    )("a0")
    assert not ok
    print(msg)

    ok, msg, data = Parser.chain(
        Parser.parse_with_regex("[a-z]*"), Parser.parse_with_regex("[0-9]*")
    )("0a")
    assert not ok
    print(msg)

    ok, msg, data = Parser.chain(
        Parser.parse_with_regex("[a-z]*[0-9]*"), Parser.parse_with_regex("[a-z]*[0-9]*")
    )("a0")
    assert ok
    assert data == "a0"

    ok, msg, data = Parser.chain(
        Parser.parse_as_float, Parser.parse_as_int
    )("1")
    assert ok
    assert data == 1
