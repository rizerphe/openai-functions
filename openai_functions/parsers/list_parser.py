"""Parser for list types"""
from __future__ import annotations
from typing import Any, List, TYPE_CHECKING, Type, TypeVar, get_args, get_origin
from typing_extensions import TypeGuard

from .abc import ArgSchemaParser

if TYPE_CHECKING:
    from ..json_type import JsonType

T = TypeVar("T")


class ListParser(ArgSchemaParser[List[T]]):
    """Parser for list types"""

    @classmethod
    def can_parse(cls, argtype: Any) -> TypeGuard[Type[List[T]]]:
        return get_origin(argtype) in [
            list,
            List,
        ]

    @property
    def argument_schema(self) -> dict[str, JsonType]:
        return {
            "type": "array",
            "items": self.parse_rec(get_args(self.argtype)[0]).argument_schema,
        }

    def parse_value(self, value: JsonType) -> List[T]:
        if not isinstance(value, list):
            raise TypeError(f"Expected list, got {value}")
        return [self.parse_rec(get_args(self.argtype)[0]).parse_value(v) for v in value]
