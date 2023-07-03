"""Parser for enum types"""
from __future__ import annotations
import enum
from typing import Any, TYPE_CHECKING, Type, TypeVar

from ..exceptions import BrokenSchemaError
from .abc import ArgSchemaParser

if TYPE_CHECKING:
    from ..json_type import JsonType
    from typing_extensions import TypeGuard

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
        schema: dict[str, JsonType] = {
            "type": "string",
            "enum": [e.name for e in self.argtype],
        }
        if self.argtype.__doc__ is not None:
            schema["description"] = self.argtype.__doc__
        return schema

    def parse_value(self, value: JsonType) -> T:
        if not isinstance(value, str):
            raise BrokenSchemaError(value, self.argument_schema)
        if value not in self.argument_schema["enum"]:  # type: ignore
            # TODO: consider using something other than JsonType for
            #       all of these, because disabling mypy is definitely
            #       not the right way to do this
            raise BrokenSchemaError(value, self.argument_schema)
        return self.argtype[value]
