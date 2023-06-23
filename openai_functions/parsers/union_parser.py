"""Parser for union types"""
from __future__ import annotations
import contextlib
from typing_extensions import TypeGuard

from .abc import ArgSchemaParser

try:
    from types import UnionType
    from typing import Any, TYPE_CHECKING, Type, Union, get_args, get_origin
except ImportError:
    # This is for Python 3.8
    from typing import (  # type: ignore
        Any,
        TYPE_CHECKING,
        Type,
        Union,
        get_args,
        get_origin,
        _GenericAlias as UnionType,
    )

if TYPE_CHECKING:
    from ..json_type import JsonType


class UnionParser(ArgSchemaParser[UnionType]):
    """Parser for union types"""

    @classmethod
    def can_parse(cls, argtype: Any) -> TypeGuard[Type[UnionType]]:
        return get_origin(argtype) is Union

    @property
    def argument_schema(self) -> dict[str, JsonType]:
        return {
            "anyOf": [self.parse_rec(t).argument_schema for t in get_args(self.argtype)]
        }

    def parse_value(self, value: JsonType) -> UnionType:
        for single_type in get_args(self.argtype):
            with contextlib.suppress(TypeError):
                return self.parse_rec(single_type).parse_value(value)
        raise TypeError(f"Expected one of {get_args(self.argtype)}, got {value}")
