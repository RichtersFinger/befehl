"""Definitions for collection-class `Parser`."""

from typing import Optional, Callable, Any, Iterable
from abc import ABC
from pathlib import Path
import re

from .common import quote_list


class Parser(ABC):
    """
    This class contains ready-to-use parsers for `Argument`s or
    `Option`s.
    """

    @staticmethod
    def first(
        *parsers: Callable[[str], tuple[bool, Optional[str], Optional[Any]]]
    ):
        """
        Returns parser that iterates the provided `parsers` and returns on
        first one returning ok.
        """
        def _(data):
            msgs = []
            for parser in parsers:
                ok, msg, _data = parser(data)
                if ok:
                    return ok, msg, _data
                msgs.append(msg)

            return False, "; ".join(msgs), None
        return _

    @staticmethod
    def chain(
        *parsers: Callable[[str], tuple[bool, Optional[str], Optional[Any]]]
    ):
        """Returns parser that iterates the provided `parsers`."""
        def _(data):
            for parser in parsers:
                ok, msg, data = parser(data)
                if not ok:
                    return ok, msg, data
            return True, None, data
        return _

    @staticmethod
    def parse_as_bool(data) -> tuple[bool, Optional[str], Optional[bool]]:
        """
        Parses `data` as a boolean. Returns ok if valid boolean.

        True values: "y", "yes", "1", "ok", "on", "enabled"
        False values: "n", "no", "0", "off", "disabled"
        """
        true = ["y", "yes", "1", "ok", "on", "enabled"]
        false = ["n", "no", "0", "off", "disabled"]
        if data.strip().lower() in true:
            return True, None, True
        if data.strip().lower() in false:
            return True, None, False
        return (
            False,
            f"input '{data}' is not a valid boolean value (y/n)",
            None,
        )

    @staticmethod
    def parse_as_int(data) -> tuple[bool, Optional[str], Optional[int]]:
        """
        Parses `data` as an integer. Returns ok if valid integer.
        """
        try:
            number = int(data)
        except ValueError:
            return False, f"input '{data}' is not an integer", None
        return True, None, number

    @staticmethod
    def parse_as_float(data) -> tuple[bool, Optional[str], Optional[float]]:
        """
        Parses `data` as a float. Returns ok if valid float.
        """
        try:
            number = float(data)
        except ValueError:
            return False, f"input '{data}' is not a float", None
        return True, None, number

    @staticmethod
    def parse_as_path(data) -> tuple[bool, Optional[str], Optional[Path]]:
        """
        Parses `data` as path. Returns ok if input exists in filesystem.
        """
        path = Path(data)
        if not path.exists():
            return False, f"path '{data}' does not exist", None
        return True, None, path

    @staticmethod
    def parse_as_file(data) -> tuple[bool, Optional[str], Optional[Path]]:
        """
        Parses `data` as file. Returns ok if input is a file.
        """
        ok, msg, data = Parser.parse_as_path(data)
        if not ok:
            return ok, msg, data
        if not data.is_file():
            return False, f"path '{data}' is not a file", None
        return True, None, data

    @staticmethod
    def parse_as_dir(data) -> tuple[bool, Optional[str], Optional[Path]]:
        """
        Parses `data` as directory. Returns ok if input is a directory.
        """
        ok, msg, data = Parser.parse_as_path(data)
        if not ok:
            return ok, msg, data
        if not data.is_dir():
            return False, f"path '{data}' is not a directory", None
        return True, None, data

    @staticmethod
    def parse_with_values(
        values: Iterable[str],
    ) -> Callable[[str], tuple[bool, Optional[str], Optional[str]]]:
        """
        Returns callable that can be used to parse strings as set of
        values. It returns ok if `data` is among the given `values`.
        """

        def _(data) -> tuple[bool, Optional[str], Optional[Path]]:
            if data not in values:
                return (
                    False,
                    f"input '{data}' is not among the allowed values: "
                    + quote_list(values),
                    None,
                )
            return True, None, data

        return _

    @staticmethod
    def parse_with_glob(
        pattern: str,
    ) -> Callable[[str], tuple[bool, Optional[str], Optional[Path]]]:
        """
        Returns callable that can be used to parse strings into paths.
        It returns ok if `data` satisfies the given glob `pattern`.
        """

        def _(data) -> tuple[bool, Optional[str], Optional[Path]]:
            path = Path(data)
            if not path.match(pattern):
                return (
                    False,
                    f"input '{data}' does not satisfy glob pattern "
                    + f"'{pattern}'",
                    None,
                )
            return True, None, path

        return _

    @staticmethod
    def parse_with_regex(
        pattern: str,
    ) -> Callable[[str], tuple[bool, Optional[str], Optional[str]]]:
        """
        Returns callable that can be used to parse strings with a regex
        and itself returns ok if `data` (full-)matches the
        given regex `pattern`.
        """
        regex_ = re.compile(pattern)

        def _(data) -> tuple[bool, Optional[str], Optional[str]]:
            if not regex_.fullmatch(data):
                return (
                    False,
                    f"input '{data}' does not match regex pattern '{pattern}'",
                    None,
                )
            return True, None, data

        return _
