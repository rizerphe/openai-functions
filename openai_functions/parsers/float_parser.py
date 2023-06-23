"""Parser for float types"""
from .atomic_type_parser import AtomicParser


class FloatParser(AtomicParser[float]):
    """Parser for float types"""

    _type = float
    schema_type_name: str = "number"
