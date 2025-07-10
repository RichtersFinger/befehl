"""Definitions for collection-class `Parsers`."""

from typing import Optional
from abc import ABC
from pathlib import Path


class Parsers(ABC):
    """
    This class contains ready-to-use parsers for `Argument`s or
    `Option`s.
    """

    @staticmethod
    def parse_path(data) -> tuple[bool, Optional[str], Optional[Path]]:
        """
        Parses input as path. Returns ok if input exists in filesystem.
        """
        if not Path(data).exists():
            return False, f"path '{data}' does not exist", None
        return True, None, Path(data)

    @staticmethod
    def parse_file(data) -> tuple[bool, Optional[str], Optional[Path]]:
        """
        Parses input as file. Returns ok if input is a file.
        """
        ok, msg, data = Parsers.parse_path(data)
        if not ok:
            return ok, msg, data
        if not data.is_file():
            return False, f"path '{data}' is not a file", None
        return True, None, data
