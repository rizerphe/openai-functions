"""Parser for null types"""
from __future__ import annotations
from types import NoneType
from typing import Any, TYPE_CHECKING, Type, TypeGuard

from .abc import ArgSchemaParser

if TYPE_CHECKING:
    from ..json_type import JsonType


class NoneParser(ArgSchemaParser[None]):
    """Parser for null types"""

    @classmethod
    def can_parse(cls, argtype: Any) -> TypeGuard[Type[None]]:
        return argtype in [None, NoneType]

    @property
    def argument_schema(self) -> dict[str, JsonType]:
        return {"type": "null"}

    def parse_value(self, value: JsonType) -> None:
        if value is not None:
            raise TypeError(f"Expected None, got {type(value)}")
