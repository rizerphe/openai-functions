"""Parser for int types"""
from __future__ import annotations
from typing import TYPE_CHECKING

from .atomic_type_parser import AtomicParser

if TYPE_CHECKING:
    from ..json_type import JsonType


class IntParser(AtomicParser[int]):
    """Parser for int types"""

    _type = int
    schema_type_name: str = "integer"

    def parse_value(self, value: JsonType) -> int:
        if isinstance(value, bool):
            # This has to happen for historical reasons
            # bool is a subclass of int, so isinstance(value, int) is True
            raise TypeError(f"Expected int, got {value}")
        return super().parse_value(value)
