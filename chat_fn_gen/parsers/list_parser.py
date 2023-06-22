"""Parser for list types"""
from __future__ import annotations
import types
from typing import Any, TYPE_CHECKING, Type, TypeGuard, TypeVar

from .abc import ArgSchemaParser

if TYPE_CHECKING:
    from ..json_type import JsonType

T = TypeVar("T")


class ListParser(ArgSchemaParser[list[T]]):
    """Parser for list types"""

    @classmethod
    def can_parse(cls, argtype: Any) -> TypeGuard[Type[list[T]]]:
        return isinstance(argtype, types.GenericAlias) and argtype.__origin__ is list

    @property
    def argument_schema(self) -> dict[str, JsonType]:
        return {
            "type": "array",
            "items": self.parse_rec(self.argtype.__args__[0]).argument_schema,
        }

    def parse_value(self, value: JsonType) -> list[T]:
        if not isinstance(value, list):
            raise TypeError(f"Expected list, got {value}")
        return [self.parse_rec(self.argtype.__args__[0]).parse_value(v) for v in value]
