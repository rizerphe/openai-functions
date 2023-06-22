"""Parser for float types"""
from __future__ import annotations
from typing import Any, TYPE_CHECKING, Type, TypeGuard

from .abc import ArgSchemaParser

if TYPE_CHECKING:
    from ..json_type import JsonType


class FloatParser(ArgSchemaParser[float]):
    """Parser for float types"""

    @classmethod
    def can_parse(cls, argtype: Any) -> TypeGuard[Type[float]]:
        return argtype is float

    @property
    def argument_schema(self) -> dict[str, JsonType]:
        return {
            "type": "number",
        }

    def parse_value(self, value: JsonType) -> float:
        if not isinstance(value, float):
            raise TypeError(f"Expected float, got {value}")
        return value
