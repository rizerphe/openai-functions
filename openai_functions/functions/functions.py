"""A module for running OpenAI functions"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, TYPE_CHECKING, runtime_checkable

if TYPE_CHECKING:
    from ..json_type import JsonType


@runtime_checkable
class OpenAIFunction(Protocol):
    """A protocol for OpenAI functions"""

    def __call__(self, arguments: dict[str, JsonType]) -> JsonType:
        ...

    @property
    def schema(self) -> JsonType:
        """Get the schema for this function"""

    @property
    def name(self) -> str:
        """Get the name of this function"""
        # This ellipsis is for Pyright #2758
        ...  # pylint: disable=unnecessary-ellipsis

    @property
    def save_return(self) -> bool:
        """Get whether to save the return value of this function"""
        ...  # pylint: disable=unnecessary-ellipsis

    @property
    def serialize(self) -> bool:
        """Get whether to continue running after this function"""
        ...  # pylint: disable=unnecessary-ellipsis

    @property
    def interpret_as_response(self) -> bool:
        """Get whether to interpret the return value of this function as a response"""
        ...  # pylint: disable=unnecessary-ellipsis


@dataclass
class FunctionResult:
    """A result of a function's execution"""

    name: str
    content: str | None
    substitute: bool = False
