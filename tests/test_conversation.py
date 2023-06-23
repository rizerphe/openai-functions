"""Test the conversation."""
import pytest

from openai_functions import FunctionWrapper, Conversation


def test_conversation_functions():
    """Test the conversation function management."""
    conversation = Conversation()

    @conversation.add_function
    def test_function():
        """Test function."""

    @conversation.add_function
    def removed_function():
        """Removed function."""

    @conversation.add_function
    def test_function_with_params(a: int, b: int):
        """Test function with params."""
        assert a == 1
        assert b == 2
        return a + b

    conversation.add_function(FunctionWrapper(lambda: None))
    conversation.remove_function("removed_function")

    assert conversation.functions_schema == [
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
        conversation.run_function(
            {
                "name": "test_function_with_params",
                "arguments": '{"a": 1, "b": 2}',
            }
        )
        == 3
    )
    with pytest.raises(ValueError):
        conversation.run_function({"name": "invalid_function", "arguments": "{}"})
