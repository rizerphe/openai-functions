"""Parser for int types"""
from .atomic_type_parser import AtomicParser


class IntParser(AtomicParser[int]):
    """Parser for int types"""

    _type = int
    schema_type_name: str = "integer"
