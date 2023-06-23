"""A module for running OpenAI functions"""
from __future__ import annotations
from functools import partial
import json
from typing import Callable, Protocol, TYPE_CHECKING, overload, runtime_checkable

import openai

from .function_wrapper import FunctionWrapper
from .openai_types import FunctionMessageType, Message

if TYPE_CHECKING:
    from .json_type import JsonType
    from .openai_types import FunctionCall, MessageType, NonFunctionMessageType


@runtime_checkable
class OpenAIFunction(Protocol):
    """A protocol for OpenAI functions"""

    def __call__(self, arguments: dict[str, JsonType]) -> JsonType:
        ...

    @property
    def schema(self) -> JsonType:
        """Get the schema for this function"""

    @property
    def name(self) -> str:  # type: ignore
        """Get the name of this function"""

    @property
    def save_return(self) -> bool:  # type: ignore
        """Get whether to save the return value of this function"""

    @property
    def serialize(self) -> bool:  # type: ignore
        """Get whether to continue running after this function"""

    @property
    def interpret_as_response(self) -> bool:  # type: ignore
        """Get whether to interpret the return value of this function as a response"""


class Runner:
    """A class for running OpenAI functions"""

    def __init__(
        self,
        functions: list[OpenAIFunction] | None = None,
        model: str = "gpt-3.5-turbo-0613",
    ) -> None:
        self.messages: list[Message] = []
        self.functions = functions or []
        self.model = model

    @property
    def functions_schema(self) -> JsonType:
        """Get the functions schema

        Returns:
            JsonType: The functions schema
        """
        return [function.schema for function in self.functions]

    def run_function(self, input_data: FunctionCall) -> JsonType:
        """Run the function

        Args:
            input_data (FunctionCall): The function call

        Returns:
            JsonType: The function output

        Raises:
            TypeError: If the input data is not a dictionary
            ValueError: If the function is not found
        """
        return self.find_function(input_data["name"])(
            json.loads(input_data["arguments"])
        )

    def _add_message(self, message: Message) -> None:
        """Add a message

        Args:
            message (Message): The message
        """
        self.messages.append(message)

    def add_message(self, message: Message | MessageType) -> None:
        """Add a message

        Args:
            message (Message | MessageType): The message
        """
        if isinstance(message, Message):
            self._add_message(message)
        else:
            self._add_message(Message(message))

    def add_messages(self, messages: list[Message | MessageType]) -> None:
        """Add messages

        Args:
            messages (list[Message | MessageType]): The messages
        """
        for message in messages:
            self.add_message(message)

    def pop_message(self, index: int = -1) -> Message:
        """Pop a message

        Args:
            index (int, optional): The index. Defaults to -1.

        Returns:
            Message: The message
        """
        return self.messages.pop(index)

    def clear_messages(self) -> None:
        """Clear the messages"""
        self.messages = []

    def _generate_message(self) -> NonFunctionMessageType:
        """Generate a response

        Returns:
            NonFunctionMessageType: The response
        """
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[message.as_dict() for message in self.messages],
            functions=self.functions_schema,
            function_call="auto",
        )
        return response["choices"][0]["message"]  # type: ignore

    def find_function(self, function_name: str) -> OpenAIFunction:
        """Find a function

        Args:
            function_name (str): The function name

        Returns:
            OpenAIFunction: The function

        Raises:
            ValueError: If the function is not found
        """
        for function in self.functions:
            if function.name == function_name:
                return function
        raise ValueError(f"Function {function_name} not found")

    def get_function_result(
        self, function: OpenAIFunction, arguments: dict[str, JsonType]
    ) -> str | None:
        """Get the result of a function

        Args:
            function (OpenAIFunction): The function
            arguments (JsonType): The arguments

        Returns:
            str | None: The result
        """
        result = function(arguments)

        if function.save_return:
            if function.serialize:
                return json.dumps(result)
            if isinstance(result, str):
                return result
            raise TypeError(f"Function {function.name} returned a non-string value")
        return None

    def substitute_last_with_function_result(self, result: str) -> None:
        """Substitute the last message with the result

        Args:
            result (str): The function result
        """
        self.pop_message()
        response: NonFunctionMessageType = {
            "role": "assistant",
            "content": result,
        }
        self.add_message(response)

    def add_function_result(
        self, function_name: str, function_result: str | None
    ) -> bool:
        """Add a function result

        Args:
            function_name (str | None): The function name
            function_result (str): The function result

        Returns:
            bool: Whether the function result was added
        """
        if function_result is None:
            return False
        response: FunctionMessageType = {
            "role": "function",
            "name": function_name,
            "content": function_result,
        }
        self.add_message(response)
        return True

    def add_or_substitute_function_result(
        self, function_name: str, function_result: str | None, substitute: bool = False
    ) -> bool:
        """Add or substitute a function result

        Args:
            function_name (str): The function name
            function_result (str): The function result
            substitute (bool): Whether to substitute the last message.

        Raises:
            TypeError: If the function returns a None value

        Returns:
            bool: Whether the function result was added
        """
        if substitute:
            if function_result is None:
                raise TypeError(f"Function {function_name} returned a None value")
            self.substitute_last_with_function_result(function_result)
            return True
        return self.add_function_result(function_name, function_result)

    def run_function_and_substitute(
        self,
        function_call: FunctionCall,
    ) -> bool:
        """Run a function, replacing the last message with the result if needed

        Args:
            function_call (FunctionCall): The function call

        Raises:
            TypeError: If the function returns a None value

        Returns:
            bool: Whether the function result was added
        """
        function = self.find_function(function_call["name"])
        function_result = self.get_function_result(
            function, json.loads(function_call["arguments"])
        )

        return self.add_or_substitute_function_result(
            function.name, function_result, function.interpret_as_response
        )

    def run_function_if_needed(self) -> bool:
        """Run a function if needed

        Returns:
            bool: Whether the function result was added
        """
        if not self.messages:
            return False

        function_call = self.messages[-1].function_call
        if not function_call:
            return False

        return self.run_function_and_substitute(function_call)

    def generate_message(self) -> Message:
        """Generate the next message

        Returns:
            Message: The response
        """
        if self.run_function_if_needed():
            return self.messages[-1]

        message = self._generate_message()
        self.add_message(message)
        return Message(message)

    def run_until_response(self) -> Message:
        """Run until a response is generated

        Returns:
            Message: The response
        """
        while True:
            message = self.generate_message()
            if message.is_final_response:
                return message

    def _add_function(self, function: OpenAIFunction) -> None:
        """Add a function

        Args:
            function (OpenAIFunction): The function
        """
        self.functions.append(function)

    @overload
    def add_function(self, function: OpenAIFunction) -> OpenAIFunction:
        ...

    @overload
    def add_function(
        self,
        function: Callable[..., JsonType],
        *,
        save_return: bool = True,
        serialize: bool = True,
        interpret_as_response: bool = False,
    ) -> Callable[..., JsonType]:
        ...

    @overload
    def add_function(
        self,
        *,
        save_return: bool = True,
        serialize: bool = True,
        interpret_as_response: bool = False,
    ) -> Callable[[Callable[..., JsonType]], Callable[..., JsonType]]:
        ...

    def add_function(
        self,
        function: OpenAIFunction | Callable[..., JsonType] | None = None,
        *,
        save_return: bool = True,
        serialize: bool = True,
        interpret_as_response: bool = False,
    ) -> (
        Callable[[Callable[..., JsonType]], Callable[..., JsonType]]
        | Callable[..., JsonType]
    ):
        """Add a function

        Args:
            function (OpenAIFunction | Callable[..., JsonType]): The function
            save_return (bool): Whether to send the return value of this
                function to the AI. Defaults to True.
            serialize (bool): Whether to serialize the return value of this
                function. Defaults to True. Otherwise, the return value must be a
                string.
            interpret_as_response (bool): Whether to interpret the return
                value of this function as a response of the agent. Defaults to False.

        Returns:
            Callable[[Callable[..., JsonType]], Callable[..., JsonType]]: A decorator
            Callable[..., JsonType]: The original function
        """
        if isinstance(function, OpenAIFunction):
            self._add_function(function)
            return function
        if callable(function):
            self._add_function(
                FunctionWrapper(
                    function, None, save_return, serialize, interpret_as_response
                )
            )
            return function

        return partial(
            self.add_function,
            save_return=save_return,
            serialize=serialize,
            interpret_as_response=interpret_as_response,
        )

    def _remove_function(self, function: str) -> None:
        """Remove a function

        Args:
            function (str): The function
        """
        self.functions = [f for f in self.functions if f.name != function]

    def remove_function(
        self, function: str | OpenAIFunction | Callable[..., JsonType]
    ) -> None:
        """Remove a function

        Args:
            function (str | OpenAIFunction | Callable[..., JsonType]): The function
        """
        if isinstance(function, str):
            self._remove_function(function)
            return
        if isinstance(function, OpenAIFunction):
            self._remove_function(function.name)
            return
        self._remove_function(function.__name__)
