"""The exceptions associated with function handling."""
from __future__ import annotations
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .json_type import JsonType


class OpenAIFunctionsError(Exception):
    """The base exception for all OpenAI Functions errors."""


class FunctionNotFoundError(OpenAIFunctionsError):
    """The function was not found in the given skillset.

    Attributes:
        function_name (str): The name of the function that was not found
    """

    def __init__(self, function_name: str) -> None:
        """Initialize the FunctionNotFoundError.

        Args:
            function_name (str): The name of the function that was not found
        """
        super().__init__(f"Function {function_name} not found.")
        self.function_name = function_name


class CannotParseTypeError(OpenAIFunctionsError):
    """This type of the argument could not be parsed.

    Attributes:
        argtype (Any): The type that could not be parsed
    """

    def __init__(self, argtype: Any) -> None:
        """Initialize the CannotParseTypeError.

        Args:
            argtype (Any): The type that could not be parsed
        """
        super().__init__(f"Cannot parse type {argtype}")
        self.argtype = argtype


class NonSerializableOutputError(OpenAIFunctionsError):
    """The function returned a non-serializable output.

    Attributes:
        result (Any): The result that was not serializable
    """

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


class InvalidJsonError(OpenAIFunctionsError):
    """OpenAI returned invalid JSON for the arguments.

    Attributes:
        response (str): The response that was not valid JSON
    """

    def __init__(self, response: str) -> None:
        """Initialize the InvalidJsonError.

        Args:
            response (str): The response that was not valid JSON
        """
        super().__init__(
            f"OpenAI returned invalid (perhaps incomplete) JSON: {response}"
        )
        self.response = response


class BrokenSchemaError(OpenAIFunctionsError):
    """The OpenAI response did not match the schema.

    Attributes:
        response (JsonType): The response that did not match the schema
        schema (JsonType): The schema that the response did not match
    """

    def __init__(self, response: JsonType, schema: JsonType) -> None:
        """Initialize the BrokenSchemaError.

        Args:
            response (JsonType): The response that did not match the schema
            schema (JsonType): The schema that the response did not match
        """
        super().__init__(
            "OpenAI returned a response that did not match the schema: "
            f"{response!r} does not match {schema}"
        )
        self.response = response
        self.schema = schema
