"""Test the runner."""
import pytest

from openai_functions import FunctionWrapper, Runner


def test_runner_functions():
    """Test the runner function management."""
    runner = Runner()

    @runner.add_function
    def test_function():
        """Test function."""

    @runner.add_function
    def removed_function():
        """Removed function."""

    @runner.add_function
    def test_function_with_params(a: int, b: int):
        """Test function with params."""
        assert a == 1
        assert b == 2
        return a + b

    runner.add_function(FunctionWrapper(lambda: None))
    runner.remove_function("removed_function")

    assert runner.functions_schema == [
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
        runner.run_function(
            {
                "name": "test_function_with_params",
                "arguments": '{"a": 1, "b": 2}',
            }
        )
        == 3
    )
    with pytest.raises(ValueError):
        runner.run_function({"name": "invalid_function", "arguments": "{}"})
