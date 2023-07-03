"""Test the function_wrapper module."""

from dataclasses import dataclass
import enum
from typing import Dict, List, Union

import pytest

from openai_functions import BrokenSchemaError, CannotParseTypeError, FunctionWrapper


def test_function_schema_generation_empty():
    """Test that the empty function schema is generated correctly."""

    def test_function():
        ...

    function_wrapper = FunctionWrapper(test_function)
    function_schema = function_wrapper.schema

    assert function_wrapper.name == "test_function"
    assert function_schema == {
        "name": "test_function",
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

    with pytest.raises(CannotParseTypeError):
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
    with pytest.raises(BrokenSchemaError):
        function_wrapper({"param1": True})


def test_dataclass():
    """Test that dataclass schemas are generated properly"""

    @dataclass
    class Container:
        """Container dataclass"""

        item: int
        priority: int = 5

    def test_function(container: Container):
        """Test function docstring."""
        assert isinstance(container, Container)
        assert container.item == 1
        assert container.priority == 2

    function_wrapper = FunctionWrapper(test_function)
    function_schema = function_wrapper.schema

    assert function_schema == {
        "name": "test_function",
        "description": "Test function docstring.",
        "parameters": {
            "type": "object",
            "properties": {
                "container": {
                    "type": "object",
                    "description": "Container dataclass",
                    "properties": {
                        "item": {"type": "integer"},
                        "priority": {"type": "integer"},
                    },
                    "required": ["item"],
                }
            },
            "required": ["container"],
        },
    }
    function_wrapper({"container": {"item": 1, "priority": 2}})
    with pytest.raises(BrokenSchemaError):
        function_wrapper({"container": 1})


def test_dataclass_with_nested_dataclass():
    """Test that dataclass schemas are generated properly"""

    @dataclass
    class Contained:
        """Contained dataclass"""

        item: int
        priority: int = 5

    @dataclass
    class Container:
        item: Contained
        priority: int = 5

    def test_function(container: Container):
        """Test function docstring.

        Args:
            container: Container dataclass
        """
        assert isinstance(container, Container)
        assert isinstance(container.item, Contained)
        assert container.item.item == 1
        assert container.item.priority == 2
        assert container.priority == 5

    function_wrapper = FunctionWrapper(test_function)
    function_schema = function_wrapper.schema

    assert function_schema == {
        "name": "test_function",
        "description": "Test function docstring.",
        "parameters": {
            "type": "object",
            "properties": {
                "container": {
                    "type": "object",
                    "description": "Container dataclass",
                    "properties": {
                        "item": {
                            "type": "object",
                            "description": "Contained dataclass",
                            "properties": {
                                "item": {"type": "integer"},
                                "priority": {"type": "integer"},
                            },
                            "required": ["item"],
                        },
                        "priority": {"type": "integer"},
                    },
                    "required": ["item"],
                }
            },
            "required": ["container"],
        },
    }
    function_wrapper({"container": {"item": {"item": 1, "priority": 2}}})


def test_invalid_dataclass_field():
    """Test that dataclass schemas are generated properly"""

    @dataclass
    class Container:
        x: object

    def test_function(container: Container):
        """Test function docstring."""

    with pytest.raises(CannotParseTypeError):
        FunctionWrapper(test_function).schema


def test_dictionary():
    """Test that dictionary schemas are generated properly"""

    def test_function(container: Dict[str, int]):
        """Test function docstring."""
        assert isinstance(container, dict)
        assert container["item"] == 1
        assert container["priority"] == 2

    function_wrapper = FunctionWrapper(test_function)
    function_schema = function_wrapper.schema

    assert function_schema == {
        "name": "test_function",
        "description": "Test function docstring.",
        "parameters": {
            "type": "object",
            "properties": {
                "container": {
                    "type": "object",
                    "additionalProperties": {"type": "integer"},
                }
            },
            "required": ["container"],
        },
    }
    function_wrapper({"container": {"item": 1, "priority": 2}})
    with pytest.raises(BrokenSchemaError):
        function_wrapper({"container": [(1, 2), (3, 4)]})


def test_array():
    """Test that array schemas are generated properly"""

    def test_function(container: List[Union[int, str]]):
        """Test function docstring."""
        assert container == [1, "test"]

    function_wrapper = FunctionWrapper(test_function)
    function_schema = function_wrapper.schema

    assert function_schema == {
        "name": "test_function",
        "description": "Test function docstring.",
        "parameters": {
            "type": "object",
            "properties": {
                "container": {
                    "type": "array",
                    "items": {"anyOf": [{"type": "integer"}, {"type": "string"}]},
                }
            },
            "required": ["container"],
        },
    }
    function_wrapper({"container": [1, "test"]})
    with pytest.raises(BrokenSchemaError):
        function_wrapper({"container": "test"})


def test_enum():
    """Test that enum schemas are generated properly"""

    class Priority(enum.Enum):
        """Priority enum"""

        LOW = 0
        MEDIUM = 1
        HIGH = 2

    def test_function(priority: Priority):
        """Test function docstring."""
        assert priority == Priority.LOW

    function_wrapper = FunctionWrapper(test_function)
    function_schema = function_wrapper.schema

    assert function_schema == {
        "name": "test_function",
        "description": "Test function docstring.",
        "parameters": {
            "type": "object",
            "properties": {
                "priority": {
                    "type": "string",
                    "enum": ["LOW", "MEDIUM", "HIGH"],
                    "description": "Priority enum",
                }
            },
            "required": ["priority"],
        },
    }
    function_wrapper({"priority": "LOW"})
    with pytest.raises(BrokenSchemaError):
        function_wrapper({"priority": 1})


def test_none():
    """Test that None schemas are generated properly"""

    def test_function(container: None):
        """Test function docstring."""
        assert container is None

    function_wrapper = FunctionWrapper(test_function)
    function_schema = function_wrapper.schema

    assert function_schema == {
        "name": "test_function",
        "description": "Test function docstring.",
        "parameters": {
            "type": "object",
            "properties": {"container": {"type": "null"}},
            "required": ["container"],
        },
    }
    function_wrapper({"container": None})
