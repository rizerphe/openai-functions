"""Parser for int types"""
from __future__ import annotations
from typing import Any, TYPE_CHECKING, Type, TypeGuard

from .abc import ArgSchemaParser

if TYPE_CHECKING:
    from ..json_type import JsonType


class IntParser(ArgSchemaParser[int]):
    """Parser for int types"""

    @classmethod
    def can_parse(cls, argtype: Any) -> TypeGuard[Type[int]]:
        return argtype is int

    @property
    def argument_schema(self) -> dict[str, JsonType]:
        return {
            "type": "integer",
        }

    def parse_value(self, value: JsonType) -> int:
        if not isinstance(value, int):
            raise TypeError(f"Expected int, got {value}")
        return value
