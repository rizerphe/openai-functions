"""Parser for null types"""
from types import NoneType

from .atomic_type_parser import AtomicParser


class IntParser(AtomicParser[NoneType]):
    """Parser for int types"""

    _type = NoneType
    schema_type_name: str = "integer"
