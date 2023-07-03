"""The exceptions associated with function handling."""


from typing import Any


class OpenAIFunctionsError(Exception):
    """The base exception for all OpenAI Functions errors."""


class FunctionNotFoundError(OpenAIFunctionsError):
    """The function was not found in the given skillset."""


class NonSerializableOutputError(OpenAIFunctionsError):
    """The function returned a non-serializable output."""

    def __init__(self, result: Any) -> None:
        """Initialize the NonSerializableOutputError.

        Args:
            result (Any): The result that was not serializable
        """
        super().__init__(
            f"The result {result} is not JSON-serializable. "
            "Set serialize=False to use str() instead."
        )
        self.result = result
