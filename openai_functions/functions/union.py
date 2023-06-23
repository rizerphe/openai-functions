"""A function set that's a union of other function sets."""
from __future__ import annotations
import contextlib
from typing import TYPE_CHECKING

from .basic_set import BasicFunctionSet
from .exceptions import FunctionNotFoundError

if TYPE_CHECKING:
    from ..json_type import JsonType
    from ..openai_types import FunctionCall
    from .functions import FunctionResult
    from .sets import FunctionSet


class UnionSkillSet(BasicFunctionSet):
    """A function set that's a union of other function sets."""

    def __init__(self, *sets: FunctionSet) -> None:
        self.sets = list(sets)
        super().__init__()

    @property
    def functions_schema(self) -> list[JsonType]:
        """Get the combined functions schema

        Returns:
            list[JsonType]: The combined functions schema
        """
        return super().functions_schema + sum(
            (function_set.functions_schema for function_set in self.sets), []
        )

    def run_function(self, input_data: FunctionCall) -> FunctionResult:
        """Run the function

        Args:
            input_data (FunctionCall): The function call

        Returns:
            FunctionResult: The function output

        Raises:
            FunctionNotFoundError: If the function is not found
        """
        for function_set in self.sets:
            with contextlib.suppress(FunctionNotFoundError):
                return function_set.run_function(input_data)
        return super().run_function(input_data)

    def add_skill(self, skill: FunctionSet) -> None:
        """Add a skill

        Args:
            skill (FunctionSet): The skill
        """
        self.sets.append(skill)
