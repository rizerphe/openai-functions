"""A module for running OpenAI functions"""
from __future__ import annotations
from dataclasses import dataclass
import json
from typing import Any, Protocol, TYPE_CHECKING, runtime_checkable

from ..exceptions import NonSerializableOutputError

if TYPE_CHECKING:
    from ..json_type import JsonType


@runtime_checkable
class OpenAIFunction(Protocol):
    """A protocol for OpenAI functions.

    Requires a __call__ method, a schema property, and a name property,
    as well as those that define the treatment of the return value.
    """

    def __call__(self, arguments: dict[str, JsonType]) -> Any:
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
    def remove_call(self) -> bool:
        """Get whether to remove the call to this function from the chat history"""
        ...  # pylint: disable=unnecessary-ellipsis

    @property
    def interpret_as_response(self) -> bool:
        """Get whether to interpret the return value of this function as a response"""
        ...  # pylint: disable=unnecessary-ellipsis


@dataclass
class RawFunctionResult:
    """A raw function result"""

    result: Any
    serialize: bool = True

    @property
    def serialized(self) -> str:
        """Get the serialized result

        Raises:
            NonSerializableOutputError: If the result cannot be serialized

        Returns:
            str: The serialized result
        """
        if self.serialize:
            try:
                return json.dumps(self.result)
            except TypeError as error:
                raise NonSerializableOutputError(self.result) from error
        return str(self.result)


@dataclass
class FunctionResult:
    """A result of a function's execution"""

    name: str
    raw_result: RawFunctionResult | None
    remove_call: bool = False
    interpret_return_as_response: bool = False

    @property
    def content(self) -> str | None:
        """Get the content of this result

        Returns:
            str | None: The content
        """
        return self.raw_result.serialized if self.raw_result else None

    @property
    def result(self) -> Any | None:
        """Get the result of this function call

        Returns:
            The raw result of the function call
        """
        if self.raw_result:
            return self.raw_result.result
        return None
