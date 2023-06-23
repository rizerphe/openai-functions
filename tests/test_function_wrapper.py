"""Test the function_wrapper module."""

from typing import Union

from openai_functions import FunctionWrapper
import pytest


def test_function_schema_generation_empty():
    """Test that the empty function schema is generated correctly."""

    def test_function():
        pass

    function_wrapper = FunctionWrapper(test_function)
    function_schema = function_wrapper.schema

    assert function_wrapper.name == "test_function"
    assert function_schema == {
        "name": "test_function",
        "description": None,
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    }


def test_function_schema_generation_docstring():
    """Test that the function schema is generated correctly with the docstring."""

    def test_function():
        """Test function docstring."""
        pass

    function_wrapper = FunctionWrapper(test_function)
    function_schema = function_wrapper.schema

    assert function_wrapper.name == "test_function"
    assert function_schema == {
        "name": "test_function",
        "description": "Test function docstring.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    }


def test_function_schema_generation_parameters():
    """Test that the function schema is generated correctly from the parameters."""

    def test_function(param1: int, param2: str, param3: bool):
        """Test function docstring."""
        pass

    function_wrapper = FunctionWrapper(test_function)
    function_schema = function_wrapper.schema

    assert function_wrapper.name == "test_function"
    assert function_schema == {
        "name": "test_function",
        "description": "Test function docstring.",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {"type": "integer"},
                "param2": {"type": "string"},
                "param3": {"type": "boolean"},
            },
            "required": ["param1", "param2", "param3"],
        },
    }


def test_function_schema_generation_parameters_with_defaults():
    """Test that the function schema is generated correctly from the docstring."""

    def test_function(param1: int, param2: str = "default", param3: bool = True):
        """Test function docstring."""
        pass

    function_wrapper = FunctionWrapper(test_function)
    function_schema = function_wrapper.schema

    assert function_wrapper.name == "test_function"
    assert function_schema == {
        "name": "test_function",
        "description": "Test function docstring.",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {"type": "integer"},
                "param2": {
                    "type": "string",
                },
                "param3": {"type": "boolean"},
            },
            "required": ["param1"],
        },
    }


def test_function_schema_generation_parameters_with_param_docs():
    """Test that the function parameters are described correctly."""

    def test_function(param1: int, param2: str, param3: bool):
        """Test function docstring.

        Args:
            param1: Parameter 1 description.
            param3: Parameter 3 description.
            param4: Parameter 4 description.
        """
        pass

    function_wrapper = FunctionWrapper(test_function)
    function_schema = function_wrapper.schema

    assert function_wrapper.name == "test_function"
    assert function_schema == {
        "name": "test_function",
        "description": "Test function docstring.",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "integer",
                    "description": "Parameter 1 description.",
                },
                "param2": {"type": "string"},
                "param3": {
                    "type": "boolean",
                    "description": "Parameter 3 description.",
                },
            },
            "required": ["param1", "param2", "param3"],
        },
    }


def test_function_schema_generation_parameters_with_union_types():
    """Test that the function schema is generated correctly from the docstring."""

    def test_function(param1: Union[int, str]):
        """Test function docstring."""
        pass

    function_wrapper = FunctionWrapper(test_function)
    function_schema = function_wrapper.schema

    assert function_wrapper.name == "test_function"
    assert "parameters" in function_schema
    assert isinstance(function_schema["parameters"], dict)
    assert "properties" in function_schema["parameters"]
    assert isinstance(function_schema["parameters"]["properties"], dict)
    assert "param1" in function_schema["parameters"]["properties"]
    assert isinstance(function_schema["parameters"]["properties"]["param1"], dict)
    assert "anyOf" in function_schema["parameters"]["properties"]["param1"]
    assert isinstance(
        function_schema["parameters"]["properties"]["param1"]["anyOf"], list
    )

    instances = function_schema["parameters"]["properties"]["param1"]["anyOf"]
    expected_instances = [
        {"type": "integer"},
        {"type": "string"},
    ]

    assert len(instances) == len(expected_instances)
    for instance in instances:
        assert instance in expected_instances


def test_function_schema_generation_invalid_parameters():
    """Test that the function schema is generated correctly from the docstring."""

    def test_function(param1: object, param2: str, param3: bool):
        """Test function docstring."""
        pass

    with pytest.raises(TypeError):
        FunctionWrapper(test_function).schema


def test_function_call():
    """Test that the function is called correctly."""

    def test_function(param1: int, param2: str, param3: bool, param4: None):
        """Test function docstring."""
        assert param1 == 1
        assert param2 == "test"
        assert param3 is True
        assert param4 is None

    function_wrapper = FunctionWrapper(test_function)
    function_wrapper({"param1": 1, "param2": "test", "param3": True, "param4": None})


def test_function_call_with_union():
    """Test that the function is called correctly."""

    def test_function(param1: Union[int, str, None]):
        """Test function docstring."""
        return param1

    function_wrapper = FunctionWrapper(test_function)

    assert function_wrapper({"param1": 1}) == 1
    assert function_wrapper({"param1": "test"}) == "test"
    assert function_wrapper({"param1": None}) is None
    with pytest.raises(TypeError):
        function_wrapper({"param1": True})
