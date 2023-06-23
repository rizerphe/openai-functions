"""Parser for string types"""
from __future__ import annotations
from typing import Any, TYPE_CHECKING, Type, TypeGuard

from .abc import ArgSchemaParser

if TYPE_CHECKING:
    from ..json_type import JsonType


class StringParser(ArgSchemaParser[str]):
    """Parser for string types"""

    @classmethod
    def can_parse(cls, argtype: Any) -> TypeGuard[Type[str]]:
        return argtype is str

    @property
    def argument_schema(self) -> dict[str, JsonType]:
        return {
            "type": "string",
        }

    def parse_value(self, value: JsonType) -> str:
        return str(value)
