"""Parser for dataclass types"""
from __future__ import annotations
import dataclasses
from typing import Any, ClassVar, Protocol, TYPE_CHECKING, Type

from ..exceptions import BrokenSchemaError
from .abc import ArgSchemaParser

if TYPE_CHECKING:
    from ..json_type import JsonType
    from typing_extensions import TypeGuard


class IsDataclass(Protocol):  # pylint: disable=too-few-public-methods
    """A protocol for checking if a class is a dataclass"""

    __dataclass_fields__: ClassVar[dict]


class DataclassParser(ArgSchemaParser[IsDataclass]):
    """Parser for dataclass types"""

    @classmethod
    def can_parse(cls, argtype: Any) -> TypeGuard[Type[IsDataclass]]:
        return dataclasses.is_dataclass(argtype)

    @property
    def required_fields(self) -> list[str]:
        """All required fields of the dataclass

        Returns:
            list[str]: The required fields of the dataclass
        """
        return [
            field.name
            for field in dataclasses.fields(self.argtype)
            if field.default is dataclasses.MISSING
        ]

    @property
    def fields(self) -> dict[str, JsonType]:
        """All fields of the dataclass, with their schemas

        Returns:
            dict[str, JsonType]: The fields of the dataclass
        """
        return {
            field.name: self.parse_rec(field.type).argument_schema
            for field in dataclasses.fields(self.argtype)
        }

    @property
    def argument_schema(self) -> dict[str, JsonType]:
        return {
            "type": "object",
            "description": self.argtype.__doc__,
            "properties": self.fields,
            "required": self.required_fields,  # type: ignore
        }

    def parse_value(self, value: JsonType) -> IsDataclass:
        if not isinstance(value, dict):
            raise BrokenSchemaError(value, self.argument_schema)
        if not all(field in value for field in self.required_fields):
            raise BrokenSchemaError(value, self.argument_schema)
        if not all(field in self.fields for field in value):
            raise BrokenSchemaError(value, self.argument_schema)
        return self.argtype(
            **{
                field.name: self.parse_rec(field.type).parse_value(value[field.name])
                for field in dataclasses.fields(self.argtype)
                if field.name in value
            }
        )
