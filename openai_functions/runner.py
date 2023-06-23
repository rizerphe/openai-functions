"""A module for running OpenAI functions"""
from __future__ import annotations
import json
from typing import Callable, Protocol, TYPE_CHECKING

import openai

from .function_wrapper import FunctionWrapper

if TYPE_CHECKING:
    from .json_type import JsonType
    from .openai_types import FunctionCall, MessageType, NonFunctionMessageType


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


class Runner:
    """A class for running OpenAI functions"""

    def __init__(
        self,
        functions: list[OpenAIFunction] | None = None,
        model: str = "gpt-3.5-turbo-0613",
    ) -> None:
        self.messages: list[MessageType] = []
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
        function_name = input_data["name"]
        for function in self.functions:
            if function.name == function_name:
                return function(json.loads(input_data["arguments"]))
        raise ValueError(f"Function {function_name} not found")

    def add_message(self, message: MessageType) -> None:
        """Add a message

        Args:
            message (MessageType): The message
        """
        self.messages.append(message)

    def generate_message(self) -> NonFunctionMessageType:
        """Generate a response

        Returns:
            NonFunctionMessageType: The response
        """
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=self.messages,
            functions=self.functions_schema,
            function_call="auto",
        )
        return response["choices"][0]["message"]  # type: ignore

    def run_until_response(self) -> NonFunctionMessageType:
        """Run until a response is generated

        Returns:
            NonFunctionMessageType: The response
        """
        while True:
            message = self.generate_message()
            self.add_message(message)
            if "function_call" not in message:
                return message
            function_result = self.run_function(message["function_call"])
            self.messages.append(
                {
                    "role": "function",
                    "name": message["function_call"]["name"],
                    "content": json.dumps(function_result),
                }
            )

    def _add_function(self, function: OpenAIFunction) -> None:
        """Add a function

        Args:
            function (OpenAIFunction): The function
        """
        self.functions.append(function)

    def add_function(self, function: OpenAIFunction | Callable[..., JsonType]) -> None:
        """Add a function

        Args:
            function (OpenAIFunction | Callable[..., JsonType]): The function
        """
        if isinstance(function, FunctionWrapper):
            self._add_function(function)
        else:
            self._add_function(FunctionWrapper(function))

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
        elif isinstance(function, FunctionWrapper):
            self._remove_function(function.name)
        else:
            self._remove_function(FunctionWrapper(function).name)
