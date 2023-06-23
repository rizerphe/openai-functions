"""A module for type definitions for OpenAI API responses"""
from __future__ import annotations
from typing import Literal, NotRequired, TypedDict


class FunctionCall(TypedDict):
    """A type for OpenAI function calls"""

    name: str
    arguments: str


class NonFunctionMessageType(TypedDict):
    """A type for OpenAI messages that are not function calls"""

    role: Literal["user", "assistant"]
    content: str | None
    function_call: NotRequired[FunctionCall]


class FunctionMessageType(TypedDict):
    """A type for OpenAI messages"""

    role: Literal["function"]
    name: str
    content: str | None


MessageType = NonFunctionMessageType | FunctionMessageType
