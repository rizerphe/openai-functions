"""Parser for enum types"""
from __future__ import annotations
import enum
from typing import Any, TYPE_CHECKING, Type, TypeVar
from typing_extensions import TypeGuard

from .abc import ArgSchemaParser

if TYPE_CHECKING:
    from ..json_type import JsonType

T = TypeVar("T", bound=enum.Enum)


class EnumParser(ArgSchemaParser[T]):
    """Parser for enum types"""

    @classmethod
    def can_parse(cls, argtype: Any) -> TypeGuard[Type[T]]:
        if not isinstance(argtype, type):
            return False
        return issubclass(argtype, enum.Enum)

    @property
    def argument_schema(self) -> dict[str, JsonType]:
        return {
            "type": "string",
            "enum": [e.value for e in self.argtype],
        }

    def parse_value(self, value: JsonType) -> T:
        if not isinstance(value, str):
            raise TypeError(f"Expected str, got {value}")
        return self.argtype(value)
