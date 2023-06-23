"""Parser for dict types"""
from __future__ import annotations
import types
from typing import Any, TYPE_CHECKING, Type, TypeGuard, TypeVar

from .abc import ArgSchemaParser

if TYPE_CHECKING:
    from ..json_type import JsonType

T = TypeVar("T")


class DictParser(ArgSchemaParser[dict[str, T]]):
    """Parser for dict types"""

    @classmethod
    def can_parse(cls, argtype: Any) -> TypeGuard[Type[dict[str, T]]]:
        return (
            isinstance(argtype, types.GenericAlias)
            and argtype.__origin__ is dict
            and argtype.__args__[0] is str
        )

    @property
    def argument_schema(self) -> dict[str, JsonType]:
        return {
            "type": "object",
            "additionalProperties": self.parse_rec(
                self.argtype.__args__[1]
            ).argument_schema,
        }

    def parse_value(self, value: JsonType) -> dict[str, T]:
        if not isinstance(value, dict):
            raise TypeError(f"Expected dict, got {value}")
        return {
            k: self.parse_rec(self.argtype.__args__[1]).parse_value(v)
            for k, v in value.items()
        }
