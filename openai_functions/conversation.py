"""A module for running OpenAI functions"""
from __future__ import annotations
from typing import Any, Callable, Literal, TYPE_CHECKING, overload

import openai

from .functions.union import UnionSkillSet
from .openai_types import (
    FinalResponseMessage,
    FinalResponseMessageType,
    ForcedFunctionCall,
    FunctionCallMessage,
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
    """A class representing a single conversation with the AI

    Contains the messages sent and received, and the skillset used.
    """

    def __init__(
        self,
        skills: list[FunctionSet] | None = None,
        model: str = "gpt-3.5-turbo-0613",
    ) -> None:
        self.messages: list[GenericMessage] = []
        self.skills = UnionSkillSet(*(skills or []))
        self.model = model

    @property
    def functions_schema(self) -> list[JsonType]:
        """Get the functions schema for the conversation

        Returns:
            list[JsonType]: The functions schema
        """
        return self.skills.functions_schema

    def _add_message(self, message: GenericMessage) -> None:
        """Add a message

        Args:
            message (GenericMessage): The message
        """
        self.messages.append(message)

    def add_message(self, message: GenericMessage | MessageType | str) -> None:
        """Add a message to the end of the conversation

        Args:
            message (GenericMessage | MessageType | str): The message
        """
        if isinstance(message, GenericMessage):
            self._add_message(message)
        else:
            self._add_message(Message(message))

    def add_messages(self, messages: list[GenericMessage | MessageType]) -> None:
        """Add multiple messages to the end of the conversation

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
        """Fully clear the messages, but keep the skillset"""
        self.messages = []

    @overload
    def _generate_message(
        self, function_call: ForcedFunctionCall
    ) -> IntermediateResponseMessageType:
        ...

    @overload
    def _generate_message(
        self, function_call: Literal["none"]
    ) -> FinalResponseMessageType:
        ...

    @overload
    def _generate_message(
        self, function_call: Literal["auto"] = "auto"
    ) -> NonFunctionMessageType:
        ...

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
        """Substitute the last message with the result of a function

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
        """Add a function execution result to the chat

        Args:
            function_result (FunctionResult): The function execution result

        Returns:
            bool: Whether the function result was added
                (whether save_return was True)
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
        """Add or substitute a function execution result

        If the function has interpret_as_response set to True, the last message,
        which is assumed to be a function call, will be replaced with the function
        execution result. Otherwise, the function execution result will be added
        to the chat.

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
                    f"Function {function_result.name} did not provide a return"
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
            bool: Whether the function result was added to the chat
                (whether save_return was True)
        """
        return self.add_or_substitute_function_result(
            self.skills.run_function(function_call)
        )

    def run_function_if_needed(self) -> bool:
        """Run a function if the last message was a function call

        Might run the function over and over again if the function
        does not save the return.

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
        """Generate the next message. Will run a function if the last message
        was a function call and the function call is not being overridden;
        if the function does not save the return a message will still be generated.

        Args:
            function_call (OpenAiFunctionCallInput): The function call

        Returns:
            GenericMessage: The response
        """
        if function_call in ["auto", "none"] and self.run_function_if_needed():
            return self.messages[-1]

        message: NonFunctionMessageType = self._generate_message(function_call)
        self.add_message(message)
        return Message(message)

    def run_until_response(
        self, allow_function_calls: bool = True
    ) -> FinalResponseMessage:
        """Run functions query the AI until a response is generated

        Args:
            allow_function_calls (bool): Whether to allow the AI to call functions

        Returns:
            FinalResponseMessage: The final response, either from the AI or a function
                that has interpret_as_response set to True
        """
        while True:
            message = self.generate_message(
                function_call="auto" if allow_function_calls else "none"
            )
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
        """Add a function to the functions available to the AI

        Args:
            function (OpenAIFunction | Callable[..., JsonType]): The function to add
            save_return (bool): Whether to send the return value of this function back
                to the AI. Defaults to True.
            serialize (bool): Whether to serialize the return value of this function.
            Defaults to True. Otherwise, the return value must be a string.
            interpret_as_response (bool): Whether to interpret the return value of this
                function as a response of the agent, replacing the function call
                message. Defaults to False.

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
        """Ask the AI a question, running until a response is generated

        Args:
            question (str): The question

        Returns:
            str: The answer to the question
        """
        self.add_message(question)
        return self.run_until_response().content

    def add_skill(self, skill: FunctionSet) -> None:
        """Add a skill to those available to the AI

        Args:
            skill (FunctionSet): The skill to add
        """
        self.skills.add_skill(skill)

    def run(self, function: str, prompt: str | None = None) -> Any:
        """Run a specified function and return the raw function result

        Args:
            function (str): The function to run
            prompt (str | None): The prompt to use

        Returns:
            The raw function result
        """
        if prompt is not None:
            self.add_message(prompt)
        # We can do type: ignore as we know we're forcing a function call
        response: FunctionCallMessage
        response = self.generate_message({"name": function})  # type: ignore
        return self.skills(response.function_call)
