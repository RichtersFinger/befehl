"""Common definitions."""

from typing import Optional, Iterable


def quote_list(data: Iterable[str], quote: Optional[str] = None) -> str:
    """Returns `data` reformatted into enumeration of quoted values."""
    return ", ".join(
        map(lambda d: f"""{quote or "'"}{d}{quote or "'"}""", data)
    )
