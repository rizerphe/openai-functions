"""A function set disabled by default that exposes a function to enable it."""
from __future__ import annotations
from typing import TYPE_CHECKING

from ..exceptions import FunctionNotFoundError
from .basic_set import BasicFunctionSet
from .functions import FunctionResult
from .functions import OpenAIFunction

if TYPE_CHECKING:
    from ..json_type import JsonType
    from ..openai_types import FunctionCall


class TogglableSet(BasicFunctionSet):
    """A function set that is disabled by default and can be enabled by the AI.

    Args:
        enable_function_name (str): The name of the function to enable the set
        enable_function_description (str, optional): The description of the enable
            function. By default no description is provided.
        functions (list[OpenAIFunction], optional): The functions in the set.
    """

    def __init__(
        self,
        enable_function_name: str,
        enable_function_description: str | None = None,
        functions: list[OpenAIFunction] | None = None,
    ) -> None:
        super().__init__(functions)
        self.enabled = False
        self.enable_function_name = enable_function_name
        self.enable_function_description = enable_function_description

    def enable(self) -> None:
        """Enable the function set."""
        self.enabled = True

    @property
    def _enable_function_schema(self) -> dict[str, JsonType]:
        """Get the schema for the enable function.

        Returns:
            dict[str, JsonType]: The schema for the enable function
        """
        schema: dict[str, JsonType] = {
            "name": self.enable_function_name,
            "parameters": {
                "type": "object",
                "properties": {},
            },
        }
        if self.enable_function_description:
            schema["description"] = self.enable_function_description
        return schema

    @property
    def functions_schema(self) -> list[JsonType]:
        """Get the functions schema, in the format OpenAI expects

        Returns:
            JsonType: The schema of all the available functions
        """
        if self.enabled:
            return super().functions_schema
        return [self._enable_function_schema]

    def run_function(self, input_data: FunctionCall) -> FunctionResult:
        """Run the function, enabling the set if the enable function is called.

        Args:
            input_data (FunctionCall): The function call

        Returns:
            FunctionResult: The function output

        Raises:
            FunctionNotFoundError: If the function is not found
        """
        if not self.enabled:
            if input_data["name"] == self.enable_function_name:
                self.enable()
                return FunctionResult(self.enable_function_name, None, True)
            raise FunctionNotFoundError(input_data["name"])
        return super().run_function(input_data)
