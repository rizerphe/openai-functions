"""Parser for union types"""
from __future__ import annotations
import types
from typing import Any, TYPE_CHECKING, Type, TypeGuard

from .abc import ArgSchemaParser

if TYPE_CHECKING:
    from ..json_type import JsonType


class UnionParser(ArgSchemaParser[types.UnionType]):
    """Parser for union types"""

    @classmethod
    def can_parse(cls, argtype: Any) -> TypeGuard[Type[types.UnionType]]:
        return isinstance(argtype, types.UnionType)

    @property
    def argument_schema(self) -> dict[str, JsonType]:
        return {
            "anyOf": [self.parse_rec(t).argument_schema for t in self.argtype.__args__],
        }

    def parse_value(self, value: JsonType) -> types.UnionType:
        for single_type in self.argtype.__args__:
            with contextlib.suppress(TypeError):
                return self.parse_rec(single_type).parse_value(value)
        raise TypeError(f"Expected one of {self.argtype.__args__}, got {value}")
