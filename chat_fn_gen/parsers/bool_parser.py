"""Parser for bool types"""
from __future__ import annotations
from typing import Any, TYPE_CHECKING, Type, TypeGuard

from .abc import ArgSchemaParser

if TYPE_CHECKING:
    from ..json_type import JsonType


class BoolParser(ArgSchemaParser[bool]):
    """Parser for bool types"""

    @classmethod
    def can_parse(cls, argtype: Any) -> TypeGuard[Type[bool]]:
        return argtype is bool

    @property
    def argument_schema(self) -> dict[str, JsonType]:
        return {
            "type": "boolean",
        }

    def parse_value(self, value: JsonType) -> bool:
        if not isinstance(value, bool):
            raise TypeError(f"Expected bool, got {value}")
        return value
