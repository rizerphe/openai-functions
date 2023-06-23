"""Test the skills."""
import pytest

from openai_functions import BasicFunctionSet, FunctionNotFoundError, FunctionWrapper


def test_skills_functions():
    """Test the skills function management."""
    skills = BasicFunctionSet()

    @skills.add_function
    def test_function():
        """Test function."""

    @skills.add_function
    def removed_function():
        """Removed function."""

    @skills.add_function
    def test_function_with_params(a: int, b: int):
        """Test function with params."""
        assert a == 1
        assert b == 2
        return a + b

    skills.add_function(FunctionWrapper(lambda: None))
    skills.remove_function("removed_function")

    assert skills.functions_schema == [
        {
            "name": "test_function",
            "description": "Test function.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
        {
            "name": "test_function_with_params",
            "description": "Test function with params.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "integer"},
                    "b": {"type": "integer"},
                },
                "required": ["a", "b"],
            },
        },
        {
            "name": "<lambda>",
            "description": None,
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    ]
    assert (
        skills.run_function(
            {
                "name": "test_function_with_params",
                "arguments": '{"a": 1, "b": 2}',
            }
        ).content
        == "3"
    )
    with pytest.raises(FunctionNotFoundError):
        skills.run_function({"name": "invalid_function", "arguments": "{}"})
