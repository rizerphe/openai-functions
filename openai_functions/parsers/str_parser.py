"""Parser for string types"""
from .atomic_type_parser import AtomicParser


class StringParser(AtomicParser[str]):
    """Parser for string types"""

    _type = str
    schema_type_name: str = "string"
