"""A module for running OpenAI functions"""
from __future__ import annotations
from abc import ABC, abstractmethod
from functools import partial
from typing import Callable, TYPE_CHECKING, overload

from .functions import FunctionResult, OpenAIFunction
from .wrapper import FunctionWrapper, WrapperConfig

if TYPE_CHECKING:
    from ..json_type import JsonType
    from ..openai_types import FunctionCall


class FunctionSet(ABC):
    """A skill set - a provider for a functions schema and a function runner"""

    @property
    @abstractmethod
    def functions_schema(self) -> list[JsonType]:
        """Get the functions schema"""

    @abstractmethod
    def run_function(self, input_data: FunctionCall) -> FunctionResult:
        """Run the function

        Args:
            input_data (FunctionCall): The function call

        Raises:
            FunctionNotFoundError: If the function is not found
        """

    def __call__(self, input_data: FunctionCall) -> JsonType:
        """Run the function with the given input data

        Args:
            input_data (FunctionCall): The input data from OpenAI

        Returns:
            JsonType: Your function's raw result
        """
        return self.run_function(input_data).result


class MutableFunctionSet(FunctionSet):
    """A skill set that can be modified - functions can be added and removed"""

    @abstractmethod
    def _add_function(self, function: OpenAIFunction) -> None:
        ...

    @overload
    def add_function(self, function: OpenAIFunction) -> OpenAIFunction:
        ...

    @overload
    def add_function(
        self,
        function: Callable[..., JsonType],
        *,
        name: str | None = None,
        description: str | None = None,
        save_return: bool = True,
        serialize: bool = True,
        remove_call: bool = False,
        interpret_as_response: bool = False,
    ) -> Callable[..., JsonType]:
        ...

    @overload
    def add_function(
        self,
        *,
        name: str | None = None,
        description: str | None = None,
        save_return: bool = True,
        serialize: bool = True,
        remove_call: bool = False,
        interpret_as_response: bool = False,
    ) -> Callable[[Callable[..., JsonType]], Callable[..., JsonType]]:
        ...

    def add_function(
        self,
        function: OpenAIFunction | Callable[..., JsonType] | None = None,
        *,
        name: str | None = None,
        description: str | None = None,
        save_return: bool = True,
        serialize: bool = True,
        remove_call: bool = False,
        interpret_as_response: bool = False,
    ) -> (
        Callable[[Callable[..., JsonType]], Callable[..., JsonType]]
        | Callable[..., JsonType]
    ):
        """Add a function

        Args:
            function (OpenAIFunction | Callable[..., JsonType]): The function
            name (str): The name of the function. Defaults to the function's name.
            description (str): The description of the function. Defaults to getting
                the short description from the function's docstring.
            save_return (bool): Whether to send the return value of this
                function to the AI. Defaults to True.
            serialize (bool): Whether to serialize the return value of this
                function. Defaults to True. Otherwise, the return value must be a
                string.
            remove_call (bool): Whether to remove the function call from the AI's
                chat history. Defaults to False.
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
                    function,
                    WrapperConfig(
                        None, save_return, serialize, remove_call, interpret_as_response
                    ),
                    name=name,
                    description=description,
                )
            )
            return function

        return partial(
            self.add_function,
            name=name,
            description=description,
            save_return=save_return,
            serialize=serialize,
            remove_call=remove_call,
            interpret_as_response=interpret_as_response,
        )

    @abstractmethod
    def _remove_function(self, name: str) -> None:
        ...

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
