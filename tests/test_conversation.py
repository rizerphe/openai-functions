from unittest.mock import MagicMock

from openai_functions import Conversation, Message


def test_add_function():
    conversation = Conversation()

    def function():
        ...

    conversation.add_function(function)
    assert conversation.skills.functions[0].name == "function"


def test_remove_function():
    conversation = Conversation()
    function = MagicMock()
    conversation.add_function(function)
    conversation.remove_function(function)
    assert function.name not in [
        function.name for function in conversation.skills.functions
    ]


def test_ask():
    conversation = Conversation()
    conversation.generate_message = MagicMock(
        return_value=Message("Hello, World!", "assistant")
    )
    response = conversation.ask("What's up?")
    assert response == "Hello, World!"


def test_run():
    conversation = Conversation()
    conversation.generate_message = MagicMock(
        return_value=Message(
            {
                "role": "assistant",
                "content": None,
                "function_call": {"name": "test_function", "args": {"test": "test"}},
            },
        )
    )
    conversation.skills = MagicMock(return_value="Test Result")
    result = conversation.run("test_function")
    conversation.skills.assert_called_once_with(
        {"name": "test_function", "args": {"test": "test"}}
    )
    assert result == "Test Result"
