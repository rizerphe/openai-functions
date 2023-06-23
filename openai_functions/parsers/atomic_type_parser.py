"""Parser for atomic json types"""
from __future__ import annotations
from abc import abstractmethod
from typing import Any, TYPE_CHECKING, Type, TypeVar

from .abc import ArgSchemaParser

if TYPE_CHECKING:
    from ..json_type import JsonType
    from typing_extensions import TypeGuard

T = TypeVar("T")


class AtomicParser(ArgSchemaParser[T]):
    """Parser for atomic json values"""

    _type: Type[T]

    @property
    @abstractmethod
    def schema_type_name(self) -> str:
        """Name of the type in the json schema"""

    @classmethod
    def can_parse(cls, argtype: Any) -> TypeGuard[Type[T]]:
        return argtype is cls._type

    @property
    def argument_schema(self) -> dict[str, JsonType]:
        return {
            "type": self.schema_type_name,
        }

    def parse_value(self, value: JsonType) -> T:
        if not isinstance(value, self._type):
            raise TypeError(f"Expected {self._type()}, got {type(value)}")
        return value
