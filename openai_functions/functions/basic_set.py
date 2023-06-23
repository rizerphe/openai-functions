"""A module for running OpenAI functions"""
from __future__ import annotations
import json
from typing import TYPE_CHECKING

from .exceptions import FunctionNotFoundError
from .functions import FunctionResult, OpenAIFunction, RawFunctionResult
from .sets import FunctionSet

if TYPE_CHECKING:
    from ..json_type import JsonType
    from ..openai_types import FunctionCall


class BasicFunctionSet(FunctionSet):
    """A skill set"""

    def __init__(
        self,
        functions: list[OpenAIFunction] | None = None,
    ) -> None:
        self.functions = functions or []

    @property
    def functions_schema(self) -> list[JsonType]:
        """Get the functions schema

        Returns:
            JsonType: The functions schema
        """
        return [function.schema for function in self.functions]

    def run_function(self, input_data: FunctionCall) -> FunctionResult:
        """Run the function

        Args:
            input_data (FunctionCall): The function call

        Returns:
            FunctionResult: The function output

        Raises:
            FunctionNotFoundError: If the function is not found
        """
        function = self.find_function(input_data["name"])
        result = self.get_function_result(function, json.loads(input_data["arguments"]))
        return FunctionResult(function.name, result, function.interpret_as_response)

    def find_function(self, function_name: str) -> OpenAIFunction:
        """Find a function

        Args:
            function_name (str): The function name

        Returns:
            OpenAIFunction: The function

        Raises:
            FunctionNotFoundError: If the function is not found
        """
        for function in self.functions:
            if function.name == function_name:
                return function
        raise FunctionNotFoundError(f"Function {function_name} not found")

    def get_function_result(
        self, function: OpenAIFunction, arguments: dict[str, JsonType]
    ) -> RawFunctionResult | None:
        """Get the result of a function

        Args:
            function (OpenAIFunction): The function
            arguments (dict[str, JsonType]): The arguments

        Returns:
            RawFunctionResult | None: The result
        """
        result = function(arguments)

        if function.save_return:
            if function.serialize:
                return RawFunctionResult(result)
            return RawFunctionResult(result)
        return None

    def _add_function(self, function: OpenAIFunction) -> None:
        """Add a function

        Args:
            function (OpenAIFunction): The function
        """
        self.functions.append(function)

    def _remove_function(self, name: str) -> None:
        """Remove a function

        Args:
            name (str): The name of the function to remove
        """
        self.functions = [f for f in self.functions if f.name != name]
