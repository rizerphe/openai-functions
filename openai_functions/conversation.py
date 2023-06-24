"""A module for running OpenAI functions"""
from __future__ import annotations
from typing import Any, Callable, TYPE_CHECKING, overload

import openai

from .functions.union import UnionSkillSet
from .openai_types import (
    FinalResponseMessage,
    FunctionMessageType,
    GenericMessage,
    IntermediateResponseMessageType,
    Message,
    is_final_response_message,
)


if TYPE_CHECKING:
    from .json_type import JsonType
    from .openai_types import (
        FunctionCall,
        MessageType,
        NonFunctionMessageType,
        OpenAiFunctionCallInput,
    )
    from .functions.functions import OpenAIFunction
    from .functions.sets import FunctionResult, FunctionSet


class Conversation:
    """A class for running OpenAI functions"""

    def __init__(
        self,
        skills: list[FunctionSet] | None = None,
        model: str = "gpt-3.5-turbo-0613",
    ) -> None:
        self.messages: list[GenericMessage] = []
        self.skills = UnionSkillSet(*(skills or []))
        self.model = model

    @property
    def functions_schema(self) -> JsonType:
        """Get the functions schema

        Returns:
            JsonType: The functions schema
        """
        return self.skills.functions_schema

    def _add_message(self, message: GenericMessage) -> None:
        """Add a message

        Args:
            message (GenericMessage): The message
        """
        self.messages.append(message)

    def add_message(self, message: GenericMessage | MessageType | str) -> None:
        """Add a message

        Args:
            message (GenericMessage | MessageType | str): The message
        """
        if isinstance(message, GenericMessage):
            self._add_message(message)
        else:
            self._add_message(Message(message))

    def add_messages(self, messages: list[GenericMessage | MessageType]) -> None:
        """Add messages

        Args:
            messages (list[GenericMessage | MessageType]): The messages
        """
        for message in messages:
            self.add_message(message)

    def pop_message(self, index: int = -1) -> GenericMessage:
        """Pop a message

        Args:
            index (int): The index. Defaults to -1.

        Returns:
            GenericMessage: The message
        """
        return self.messages.pop(index)

    def clear_messages(self) -> None:
        """Clear the messages"""
        self.messages = []

    def _generate_message(
        self, function_call: OpenAiFunctionCallInput = "auto"
    ) -> NonFunctionMessageType:
        """Generate a response

        Args:
            function_call (OpenAiFunctionCallInput): The function call.

        Returns:
            NonFunctionMessageType: The response
        """
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[message.as_dict() for message in self.messages],
            functions=self.functions_schema,
            function_call=function_call,
        )
        return response["choices"][0]["message"]  # type: ignore

    def substitute_last_with_function_result(self, result: str) -> None:
        """Substitute the last message with the result

        Args:
            result (str): The function result
        """
        self.pop_message()
        response: NonFunctionMessageType = {
            "role": "assistant",
            "content": result,
        }
        self.add_message(response)

    def add_function_result(self, function_result: FunctionResult) -> bool:
        """Add a function result

        Args:
            function_result (FunctionResult): The function result

        Returns:
            bool: Whether the function result was added
        """
        if function_result.content is None:
            return False
        response: FunctionMessageType = {
            "role": "function",
            "name": function_result.name,
            "content": function_result.content,
        }
        self.add_message(response)
        return True

    def add_or_substitute_function_result(
        self, function_result: FunctionResult
    ) -> bool:
        """Add or substitute a function result

        Args:
            function_result (FunctionResult): The function result

        Raises:
            TypeError: If the function returns a None value

        Returns:
            bool: Whether the function result was added
        """
        if function_result.substitute:
            if function_result.content is None:
                raise TypeError(
                    f"Function {function_result.name} returned a None value"
                )
            self.substitute_last_with_function_result(function_result.content)
            return True
        return self.add_function_result(function_result)

    def run_function_and_substitute(
        self,
        function_call: FunctionCall,
    ) -> bool:
        """Run a function, replacing the last message with the result if needed

        Args:
            function_call (FunctionCall): The function call

        Raises:
            TypeError: If the function returns a None value

        Returns:
            bool: Whether the function result was added
        """
        return self.add_or_substitute_function_result(
            self.skills.run_function(function_call)
        )

    def run_function_if_needed(self) -> bool:
        """Run a function if needed

        Returns:
            bool: Whether the function result was added
        """
        if not self.messages:
            return False

        function_call = self.messages[-1].function_call
        if not function_call:
            return False

        return self.run_function_and_substitute(function_call)

    def generate_message(
        self, function_call: OpenAiFunctionCallInput = "auto"
    ) -> GenericMessage:
        """Generate the next message

        Args:
            function_call (OpenAiFunctionCallInput): The function call

        Returns:
            GenericMessage: The response
        """
        if self.run_function_if_needed():
            return self.messages[-1]

        message = self._generate_message(function_call)
        self.add_message(message)
        return Message(message)

    def run_until_response(self) -> FinalResponseMessage:
        """Run until a response is generated

        Returns:
            FinalResponseMessage: The response
        """
        while True:
            message = self.generate_message()
            if is_final_response_message(message):
                return message

    @overload
    def add_function(self, function: OpenAIFunction) -> OpenAIFunction:
        ...

    @overload
    def add_function(
        self,
        function: Callable[..., JsonType],
        *,
        save_return: bool = True,
        serialize: bool = True,
        interpret_as_response: bool = False,
    ) -> Callable[..., JsonType]:
        ...

    @overload
    def add_function(
        self,
        *,
        save_return: bool = True,
        serialize: bool = True,
        interpret_as_response: bool = False,
    ) -> Callable[[Callable[..., JsonType]], Callable[..., JsonType]]:
        ...

    def add_function(
        self,
        function: OpenAIFunction | Callable[..., JsonType] | None = None,
        *,
        save_return: bool = True,
        serialize: bool = True,
        interpret_as_response: bool = False,
    ) -> (
        Callable[[Callable[..., JsonType]], Callable[..., JsonType]]
        | Callable[..., JsonType]
    ):
        """Add a function

        Args:
            function (OpenAIFunction | Callable[..., JsonType]): The function
            save_return (bool): Whether to send the return value of this
                function to the AI. Defaults to True.
            serialize (bool): Whether to serialize the return value of this
                function. Defaults to True. Otherwise, the return value must be a
                string.
            interpret_as_response (bool): Whether to interpret the return
                value of this function as a response of the agent. Defaults to False.

        Returns:
            Callable[[Callable[..., JsonType]], Callable[..., JsonType]]: A decorator
            Callable[..., JsonType]: The original function
        """
        if function is None:
            return self.skills.add_function(
                save_return=save_return,
                serialize=serialize,
                interpret_as_response=interpret_as_response,
            )
        return self.skills.add_function(
            function,
            save_return=save_return,
            serialize=serialize,
            interpret_as_response=interpret_as_response,
        )

    def remove_function(
        self, function: str | OpenAIFunction | Callable[..., JsonType]
    ) -> None:
        """Remove a function

        Args:
            function (str | OpenAIFunction | Callable[..., JsonType]): The function
        """
        self.skills.remove_function(function)

    def ask(self, question: str) -> str:
        """Ask the AI a question

        Args:
            question (str): The question

        Returns:
            str: The answer to the question
        """
        self.add_message(question)
        return self.run_until_response().content

    def add_skill(self, skill: FunctionSet) -> None:
        """Add a skill

        Args:
            skill (FunctionSet): The skill to add
        """
        self.skills.add_skill(skill)

    def run(self, function: str, prompt: str) -> Any:
        """Run a specified function and return the raw function result

        Args:
            prompt (str): The prompt to use
            function (str): The function to run

        Returns:
            The raw function result
        """
        self.add_message(prompt)
        # We can do type: ignore as we know we're forcing a function call
        response: IntermediateResponseMessageType
        response = self._generate_message({"name": function})  # type: ignore
        return self.skills(response["function_call"])
