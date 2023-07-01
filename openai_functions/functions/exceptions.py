"""The exceptions associated with function handling."""


class OpenAIFunctionsError(Exception):
    """The base exception for all OpenAI Functions errors."""


class FunctionNotFoundError(OpenAIFunctionsError):
    """The function was not found in the given skillset."""


class NonSerializableOutputError(OpenAIFunctionsError):
    """The function did not return a string."""
