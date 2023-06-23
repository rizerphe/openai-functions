"""Parser for bool types"""
from .atomic_type_parser import AtomicParser


class BoolParser(AtomicParser[bool]):
    """Parser for bool types"""

    _type = bool
    schema_type_name: str = "boolean"
