"""Parser for dataclass types"""
from __future__ import annotations
import dataclasses
from typing import Any, ClassVar, Protocol, TYPE_CHECKING, Type
from typing_extensions import TypeGuard

from .abc import ArgSchemaParser

if TYPE_CHECKING:
    from ..json_type import JsonType


class IsDataclass(Protocol):  # pylint: disable=too-few-public-methods
    """A protocol for checking if a class is a dataclass"""

    __dataclass_fields__: ClassVar[dict]


class DataclassParser(ArgSchemaParser[IsDataclass]):
    """Parser for dataclass types"""

    @classmethod
    def can_parse(cls, argtype: Any) -> TypeGuard[Type[IsDataclass]]:
        return dataclasses.is_dataclass(argtype)

    @property
    def argument_schema(self) -> dict[str, JsonType]:
        return {
            "type": "object",
            "description": self.argtype.__doc__,
            "properties": {
                field.name: self.parse_rec(field.type).argument_schema
                for field in dataclasses.fields(self.argtype)
            },
            "required": [
                field.name
                for field in dataclasses.fields(self.argtype)
                if field.default is dataclasses.MISSING
            ],
        }

    def parse_value(self, value: JsonType) -> IsDataclass:
        if not isinstance(value, dict):
            raise TypeError(f"Expected dict, got {value}")
        return self.argtype(
            **{
                field.name: self.parse_rec(field.type).parse_value(value[field.name])
                for field in dataclasses.fields(self.argtype)
            }
        )
