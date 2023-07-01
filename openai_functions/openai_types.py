"""A module for type definitions for OpenAI API responses"""
from __future__ import annotations
from typing import (
    Literal,
    Protocol,
    TYPE_CHECKING,
    TypedDict,
    Union,
    overload,
    runtime_checkable,
)

if TYPE_CHECKING:
    from typing_extensions import TypeGuard


class FunctionCall(TypedDict):
    """A container for OpenAI function calls

    Attributes:
        name (str): The name of the function
        arguments (str): The arguments of the function, in JSON format
    """

    name: str
    arguments: str


class FinalResponseMessageType(TypedDict):
    """A type for OpenAI messages that are final responses"""

    role: Literal["assistant"]
    content: str


class UserMessageType(TypedDict):
    """A type for OpenAI messages that are user messages"""

    role: Literal[
        "system",
        "user",
    ]
    content: str


ContentfulMessageType = Union[FinalResponseMessageType, UserMessageType]


class IntermediateResponseMessageType(TypedDict):
    """A type for OpenAI messages that are intermediate responses"""

    role: Literal["assistant"]
    content: None
    function_call: FunctionCall


NonFunctionMessageType = Union[ContentfulMessageType, IntermediateResponseMessageType]


class FunctionMessageType(TypedDict):
    """A type for OpenAI messages"""

    role: Literal["function"]
    name: str
    content: str | None


MessageType = Union[NonFunctionMessageType, FunctionMessageType]


class Message:
    """A container for OpenAI messages"""

    @overload
    def __init__(self, message: MessageType) -> None:
        ...

    @overload
    def __init__(self, message: str) -> None:
        ...

    @overload
    def __init__(
        self, message: str, role: Literal["system", "user", "assistant"]
    ) -> None:
        ...

    def __init__(
        self,
        message: MessageType | str,
        role: Literal["system", "user", "assistant"] = "user",
    ):
        if isinstance(message, str):
            if role == "assistant":  # We have to split this up because of mypy
                self.message: MessageType = {"role": role, "content": message}
            else:
                self.message = {
                    "role": role,
                    "content": message,
                }
        else:
            self.message = message

    @property
    def content(self) -> str | None:
        """Get the content of the message

        Returns:
            str | None: The content of the message
        """
        return self.message["content"]

    @property
    def role(self) -> Literal["system", "user", "assistant", "function"]:
        """Get the role of the message

        Returns:
            Literal["system", "user", "assistant", "function"]: The role of the message
        """
        return self.message["role"]

    @property
    def is_function_call(self) -> bool:
        """Check if the message is a function call

        Returns:
            bool: Whether the message is a function call
        """
        return self.role == "assistant" and "function_call" in self.message

    @property
    def function_call(self) -> FunctionCall | None:
        """Get the function call

        Returns:
            FunctionCall | None: The function call
        """
        if self.message["role"] == "assistant":
            if self.message.get("content") is not None:
                return None
            return self.message.get("function_call")  # type: ignore
        return None

    @property
    def is_final_response(self) -> bool:
        """Check if the message is a final response

        Returns:
            bool: Whether the message is a final response
        """
        return self.role == "assistant" and self.content is not None

    def as_dict(self) -> MessageType:
        """Get the message as a dictionary

        Returns:
            MessageType: The message
        """
        return self.message

    def __repr__(self) -> str:
        if self.is_function_call:
            return f"FunctionCall({self.function_call!r})"
        return f"Message({self.message['content']!r}, {self.message['role']!r})"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Message)
            and self.content == other.content
            and self.role == other.role
            and self.function_call == other.function_call
        )

    def __hash__(self) -> int:
        return hash((self.content, self.role))


@runtime_checkable
class GenericMessage(Protocol):
    """A container protocol for OpenAI messages"""

    message: MessageType

    @overload
    def __init__(self, message: MessageType) -> None:
        ...

    @overload
    def __init__(self, message: str) -> None:
        ...

    @overload
    def __init__(
        self, message: str, role: Literal["system", "user", "assistant"]
    ) -> None:
        ...

    def __init__(
        self,
        message: MessageType | str,
        role: Literal["system", "user", "assistant"] = "user",
    ):
        ...

    @property
    def content(self) -> str | None:
        """Get the content of the message"""

    @property
    def role(self) -> Literal["system", "user", "assistant", "function"]:
        """Get the role of the message"""
        ...  # pylint: disable=unnecessary-ellipsis

    @property
    def is_function_call(self) -> bool:
        """Check if the message is a function call"""
        ...  # pylint: disable=unnecessary-ellipsis

    @property
    def function_call(self) -> FunctionCall | None:
        """Get the function call"""

    @property
    def is_final_response(self) -> bool:
        """Check if the message is a final response"""
        ...  # pylint: disable=unnecessary-ellipsis

    def as_dict(self) -> MessageType:
        """Get the message as a dictionary"""
        ...  # pylint: disable=unnecessary-ellipsis

    def __hash__(self) -> int:
        ...


class FinalResponseMessage(GenericMessage, Protocol):
    """A container for OpenAI final response messages

    Inherited from GenericMessage, acts the same, just restricts
    the message to have content and not be a function call
    """

    message: FinalResponseMessageType  # type: ignore

    @property
    def content(self) -> str:
        """Get the content of the message"""
        # This ellipsis is for Pyright #2758
        ...  # pylint: disable=unnecessary-ellipsis

    @property
    def function_call(self) -> None:
        """Get the function call"""

    @property
    def is_final_response(self) -> Literal[True]:
        """Check if the message is a final response"""
        ...  # pylint: disable=unnecessary-ellipsis


class FunctionCallMessage(GenericMessage, Protocol):
    """A container for OpenAI function call messages"""

    message: IntermediateResponseMessageType

    @property
    def content(self) -> None:
        """Get the content of the message"""

    @property
    def function_call(self) -> FunctionCall:
        """Get the function call"""
        ...  # pylint: disable=unnecessary-ellipsis

    @property
    def is_final_response(self) -> Literal[False]:
        """Check if the message is a final response"""
        ...  # pylint: disable=unnecessary-ellipsis


def is_final_response_message(
    message: GenericMessage,
) -> TypeGuard[FinalResponseMessage]:
    """Check if a message is a final response message

    Args:
        message (GenericMessage): The message to check

    Returns:
        TypeGuard[FinalResponseMessage]: Whether the message is a final response message
    """
    return message.is_final_response


class ForcedFunctionCall(TypedDict):
    """A type for forced function calls"""

    name: str


OpenAiFunctionCallInput = Union[ForcedFunctionCall, Literal["auto", "none"]]
