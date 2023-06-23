"""Parser for dict types"""
from __future__ import annotations
from typing import Any, Dict, TYPE_CHECKING, Type, TypeVar, get_args, get_origin
from typing_extensions import TypeGuard

from .abc import ArgSchemaParser

if TYPE_CHECKING:
    from ..json_type import JsonType

T = TypeVar("T")


class DictParser(ArgSchemaParser[Dict[str, T]]):
    """Parser for dict types"""

    @classmethod
    def can_parse(cls, argtype: Any) -> TypeGuard[Type[Dict[str, T]]]:
        return (
            get_origin(argtype)
            in [
                dict,
                Dict,
            ]
            and get_args(argtype)[0] is str
        )

    @property
    def argument_schema(self) -> Dict[str, JsonType]:
        return {
            "type": "object",
            "additionalProperties": self.parse_rec(
                get_args(self.argtype)[1]
            ).argument_schema,
        }

    def parse_value(self, value: JsonType) -> Dict[str, T]:
        if not isinstance(value, dict):
            raise TypeError(f"Expected dict, got {value}")
        return {
            k: self.parse_rec(get_args(self.argtype)[1]).parse_value(v)
            for k, v in value.items()
        }
