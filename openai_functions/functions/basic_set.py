"""A module for running OpenAI functions"""
from __future__ import annotations
import json
from typing import TYPE_CHECKING

from ..exceptions import FunctionNotFoundError, InvalidJsonError
from .functions import FunctionResult, OpenAIFunction, RawFunctionResult
from .sets import MutableFunctionSet

if TYPE_CHECKING:
    from ..json_type import JsonType
    from ..openai_types import FunctionCall


class BasicFunctionSet(MutableFunctionSet):
    """A skill set - a set of OpenAIFunction objects ready to be called.
    Inherited from `MutableFunctionSet`, therefore you can add and remove functions
    by using the `@add_function` and `remove_function` methods.

    Args:
        functions (list[OpenAIFunction] | None): The functions to initialize with.
    """

    def __init__(
        self,
        functions: list[OpenAIFunction] | None = None,
    ) -> None:
        self.functions = functions or []

    @property
    def functions_schema(self) -> list[JsonType]:
        """Get the functions schema, in the format OpenAI expects

        Returns:
            JsonType: The schema of all the available functions
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
        try:
            arguments = json.loads(input_data["arguments"])
        except json.decoder.JSONDecodeError as e:
            raise InvalidJsonError(input_data["arguments"]) from e
        result = self.get_function_result(function, arguments)
        return FunctionResult(
            function.name, result, function.remove_call, function.interpret_as_response
        )

    def find_function(self, function_name: str) -> OpenAIFunction:
        """Find a function in the skillset

        Args:
            function_name (str): The function name

        Returns:
            OpenAIFunction: The function of the given name

        Raises:
            FunctionNotFoundError: If the function is not found
        """
        for function in self.functions:
            if function.name == function_name:
                return function
        raise FunctionNotFoundError(function_name)

    def get_function_result(
        self, function: OpenAIFunction, arguments: dict[str, JsonType]
    ) -> RawFunctionResult | None:
        """Get the result of a function's execution

        Args:
            function (OpenAIFunction): The function to run
            arguments (dict[str, JsonType]): The arguments to run the function with

        Returns:
            RawFunctionResult | None: The result of the function, or None if the
                function does not save its return value
        """
        result = function(arguments)

        if function.save_return:
            return RawFunctionResult(result, serialize=function.serialize)
        return None

    def _add_function(self, function: OpenAIFunction) -> None:
        """Add a function to the skillset

        Args:
            function (OpenAIFunction): The function
        """
        self.functions.append(function)

    def _remove_function(self, name: str) -> None:
        """Remove a function from the skillset

        Args:
            name (str): The name of the function to remove
        """
        self.functions = [f for f in self.functions if f.name != name]
