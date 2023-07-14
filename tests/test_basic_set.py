from dataclasses import dataclass
import json
from typing import Any, Callable

import pytest

from openai_functions.exceptions import FunctionNotFoundError, InvalidJsonError
from openai_functions.functions.basic_set import BasicFunctionSet
from openai_functions.json_type import JsonType
from openai_functions.openai_types import FunctionCall


@dataclass
class MockOpenAIFunction:
    name: str
    schema: JsonType
    function: Callable[..., JsonType]
    save_return: bool
    serialize: bool
    remove_call: bool
    interpret_as_response: bool

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.function(*args, **kwds)


def test_init_functions() -> None:
    functions: list[MockOpenAIFunction] = [
        MockOpenAIFunction(
            name="test_function",
            schema={"type": "object", "properties": {"arg1": {"type": "string"}}},
            function=lambda args: args["arg1"],
            save_return=True,
            serialize=False,
            remove_call=True,
            interpret_as_response=False,
        )
    ]
    function_set = BasicFunctionSet(functions=functions)
    assert function_set.functions == functions


def test_init_no_functions() -> None:
    function_set = BasicFunctionSet()
    assert function_set.functions == []


def test_functions_schema() -> None:
    functions = [
        MockOpenAIFunction(
            name="test_function",
            schema={"type": "object", "properties": {"arg1": {"type": "string"}}},
            function=lambda args: args["arg1"],
            save_return=True,
            serialize=False,
            remove_call=True,
            interpret_as_response=False,
        )
    ]
    function_set = BasicFunctionSet(functions=functions)
    expected_schema = [{"type": "object", "properties": {"arg1": {"type": "string"}}}]
    assert function_set.functions_schema == expected_schema


def test_run_function() -> None:
    functions = [
        MockOpenAIFunction(
            name="test_function",
            schema={"type": "object", "properties": {"arg1": {"type": "string"}}},
            function=lambda args: args["arg1"],
            save_return=True,
            serialize=False,
            remove_call=True,
            interpret_as_response=False,
        )
    ]
    function_set = BasicFunctionSet(functions=functions)
    input_data = FunctionCall(
        name="test_function", arguments=json.dumps({"arg1": "hello"})
    )
    result = function_set.run_function(input_data)
    assert result.name == "test_function"
    assert result.result == "hello"
    assert result.remove_call is True
    assert result.interpret_return_as_response is False


def test_run_function_invalid_json() -> None:
    functions = [
        MockOpenAIFunction(
            name="test_function",
            schema={"type": "object", "properties": {"arg1": {"type": "string"}}},
            function=lambda args: args["arg1"],
            save_return=True,
            serialize=False,
            remove_call=True,
            interpret_as_response=False,
        )
    ]
    function_set = BasicFunctionSet(functions=functions)
    input_data = FunctionCall(name="test_function", arguments="invalid json")
    with pytest.raises(InvalidJsonError):
        function_set.run_function(input_data)


def test_run_function_function_not_found() -> None:
    function_set = BasicFunctionSet()
    input_data = FunctionCall(
        name="test_function", arguments=json.dumps({"arg1": "hello"})
    )
    with pytest.raises(FunctionNotFoundError):
        function_set.run_function(input_data)


def test_find_function() -> None:
    functions = [
        MockOpenAIFunction(
            name="test_function",
            schema={"type": "object", "properties": {"arg1": {"type": "string"}}},
            function=lambda args: args["arg1"],
            save_return=True,
            serialize=False,
            remove_call=True,
            interpret_as_response=False,
        )
    ]
    function_set = BasicFunctionSet(functions=functions)
    function = function_set.find_function("test_function")
    assert function.name == "test_function"


def test_find_function_not_found() -> None:
    function_set = BasicFunctionSet()
    with pytest.raises(FunctionNotFoundError):
        function_set.find_function("test_function")


def test_get_function_result() -> None:
    functions = [
        MockOpenAIFunction(
            name="test_function",
            schema={"type": "object", "properties": {"arg1": {"type": "string"}}},
            function=lambda args: args["arg1"],
            save_return=True,
            serialize=False,
            remove_call=True,
            interpret_as_response=False,
        )
    ]
    function_set = BasicFunctionSet(functions=functions)
    function = function_set.find_function("test_function")
    arguments = {"arg1": "hello"}
    result = function_set.get_function_result(function, arguments)
    assert result is not None
    assert result.result == "hello"


def test_get_function_result_no_save_return() -> None:
    functions = [
        MockOpenAIFunction(
            name="test_function",
            schema={"type": "object", "properties": {"arg1": {"type": "string"}}},
            function=lambda args: None,
            save_return=False,
            serialize=False,
            remove_call=True,
            interpret_as_response=False,
        )
    ]
    function_set = BasicFunctionSet(functions=functions)
    function = function_set.find_function("test_function")
    arguments = {"arg1": "hello"}
    result = function_set.get_function_result(function, arguments)
    assert result is None


def test_add_function() -> None:
    function_set = BasicFunctionSet()
    function = MockOpenAIFunction(
        name="test_function",
        schema={"type": "object", "properties": {"arg1": {"type": "string"}}},
        function=lambda args: args["arg1"],
        save_return=True,
        serialize=False,
        remove_call=True,
        interpret_as_response=False,
    )
    function_set.add_function(function)
    assert function_set.functions == [function]


def test_remove_function() -> None:
    functions = [
        MockOpenAIFunction(
            name="test_function",
            schema={"type": "object", "properties": {"arg1": {"type": "string"}}},
            function=lambda args: args["arg1"],
            save_return=True,
            serialize=False,
            remove_call=True,
            interpret_as_response=False,
        )
    ]
    function_set = BasicFunctionSet(functions=functions)
    function_set.remove_function("test_function")
    assert function_set.functions == []

