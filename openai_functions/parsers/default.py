"""Default parsers for ArgSchema."""
from __future__ import annotations
from typing import TYPE_CHECKING, Type

from .bool_parser import BoolParser
from .dataclass_parser import DataclassParser
from .dict_parser import DictParser
from .enum_parser import EnumParser
from .float_parser import FloatParser
from .int_parser import IntParser
from .list_parser import ListParser
from .none_parser import NoneParser
from .str_parser import StringParser
from .union_parser import UnionParser

if TYPE_CHECKING:
    from .abc import ArgSchemaParser


defargparsers: list[Type[ArgSchemaParser]] = [
    BoolParser,
    DataclassParser,
    DictParser,
    EnumParser,
    FloatParser,
    IntParser,
    ListParser,
    NoneParser,
    StringParser,
    UnionParser,
]
