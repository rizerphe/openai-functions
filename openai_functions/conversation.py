"""A module for running OpenAI functions"""
from __future__ import annotations
import time
from typing import Any, Callable, Literal, TYPE_CHECKING, overload

import openai
import openai.error

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
        self, function_call: ForcedFunctionCall, retries: int | None = 1
    ) -> IntermediateResponseMessageType:
        ...

    @overload
    def _generate_message(
        self, function_call: Literal["none"], retries: int | None = 1
    ) -> FinalResponseMessageType:
        ...

    @overload
    def _generate_message(
        self, function_call: Literal["auto"] = "auto", retries: int | None = 1
    ) -> NonFunctionMessageType:
        ...

    def _generate_message(
        self, function_call: OpenAiFunctionCallInput = "auto", retries: int | None = 1
    ) -> NonFunctionMessageType:
        """Generate a response, retrying if necessary

        Args:
            function_call (OpenAiFunctionCallInput): The function call.
            retries (int | None): The number of retries. Defaults to 4.
                Will retry indefinitely if None.

        Raises:
            openai.error.RateLimitError: If the rate limit is exceeded

        Returns:
            NonFunctionMessageType: The response
        """
        if retries is None:
            retries = -1
        while True:
            try:
                response = self._generate_raw_message(function_call)
            except openai.error.RateLimitError as error:
                if retries == 0:
                    raise
                retries -= 1
                time.sleep(self._retry_time_from_headers(error.headers))
            else:
                return response["choices"][0]["message"]  # type: ignore

    def _parse_retry_time(self, wait_for: str) -> float:
        """Parse the time returned by an x-ratelimit-reset-requests header

        Args:
            wait_for (str): The time

        Returns:
            float: The time to the next reset
        """
        return float(wait_for[:-1]) * {"s": 1, "m": 60, "h": 3600}[wait_for[-1]]

    def _retry_time_from_headers(self, headers: dict[str, str]) -> float:
        """Get the time returned by the headers of an 429 reply

        Args:
            headers (dict[str, str]): The headers of the reply

        Returns:
            float: The time to wait for before retrying
        """
        return self._parse_retry_time(headers["x-ratelimit-reset-requests"]) / int(
            headers["x-ratelimit-limit-requests"]
        )

    def _generate_raw_message(self, function_call: OpenAiFunctionCallInput) -> Any:
        """Generate a raw OpenAI response

        Args:
            function_call (OpenAiFunctionCallInput): The function call.

        Returns:
            The raw OpenAI response
        """
        return openai.ChatCompletion.create(
            model=self.model,
            messages=[message.as_dict() for message in self.messages],
            functions=self.functions_schema,
            function_call=function_call,
        )

    def remove_function_call(self, function_name: str) -> None:
        """Remove a function call from the messages, if it is the last message

        Args:
            function_name (str): The function name
        """
        if (
            self.messages[-1].function_call
            and self.messages[-1].function_call["name"] == function_name
        ):
            self.pop_message()

    def _add_function_result(self, function_result: FunctionResult) -> bool:
        """Add a function execution result to the chat

        Args:
            function_result (FunctionResult): The function execution result

        Returns:
            bool: Whether the function result was added
                (whether save_return was True)
        """
        if function_result.content is None:
            return False
        if function_result.interpret_return_as_response:
            self._add_function_result_as_response(function_result.content)
        else:
            self._add_function_result_as_function_call(function_result)
        return True

    def _add_function_result_as_response(self, function_result: str) -> None:
        """Add a function execution result to the chat as an assistant response

        Args:
            function_result (str): The function execution result
        """
        response: FinalResponseMessageType = {
            "role": "assistant",
            "content": function_result,
        }
        self.add_message(response)

    def _add_function_result_as_function_call(
        self, function_result: FunctionResult
    ) -> None:
        """Add a function execution result to the chat as a function call

        Args:
            function_result (FunctionResult): The function execution result
        """
        response: FunctionMessageType = {
            "role": "function",
            "name": function_result.name,
            "content": function_result.content,
        }
        self.add_message(response)

    def add_function_result(self, function_result: FunctionResult) -> bool:
        """Add a function execution result

        If the function has a return value (save_return is True), it will be added to
        the chat. The function call will be removed depending on the remove_call
        attribute, and the function result will be interpreted as a response or a
        function call depending on the interpret_return_as_response attribute.

        Args:
            function_result (FunctionResult): The function result

        Returns:
            bool: Whether the function result was added
        """
        if function_result.remove_call:
            self.remove_function_call(function_result.name)
        return self._add_function_result(function_result)

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
        return self.add_function_result(self.skills.run_function(function_call))

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
        self, function_call: OpenAiFunctionCallInput = "auto", retries: int | None = 1
    ) -> GenericMessage:
        """Generate the next message. Will run a function if the last message
        was a function call and the function call is not being overridden;
        if the function does not save the return a message will still be generated.

        Args:
            function_call (OpenAiFunctionCallInput): The function call
            retries (int | None): The number of retries; if None, will retry
                indefinitely

        Returns:
            GenericMessage: The response
        """
        if function_call in ["auto", "none"] and self.run_function_if_needed():
            return self.messages[-1]

        message: NonFunctionMessageType = self._generate_message(function_call, retries)
        self.add_message(message)
        return Message(message)

    def run_until_response(
        self, allow_function_calls: bool = True, retries: int | None = 1
    ) -> FinalResponseMessage:
        """Run functions query the AI until a response is generated

        Args:
            allow_function_calls (bool): Whether to allow the AI to call functions
            retries (int | None): The number of retries; if None, will retry
                indefinitely

        Returns:
            FinalResponseMessage: The final response, either from the AI or a function
                that has interpret_as_response set to True
        """
        while True:
            message = self.generate_message(
                function_call="auto" if allow_function_calls else "none",
                retries=retries,
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
        name: str | None = None,
        description: str | None = None,
        save_return: bool = True,
        serialize: bool = True,
        remove_call: bool = False,
        interpret_as_response: bool = False,
    ) -> Callable[..., JsonType]:
        ...

    @overload
    def add_function(
        self,
        *,
        name: str | None = None,
        description: str | None = None,
        save_return: bool = True,
        serialize: bool = True,
        remove_call: bool = False,
        interpret_as_response: bool = False,
    ) -> Callable[[Callable[..., JsonType]], Callable[..., JsonType]]:
        ...

    def add_function(
        self,
        function: OpenAIFunction | Callable[..., JsonType] | None = None,
        *,
        name: str | None = None,
        description: str | None = None,
        save_return: bool = True,
        serialize: bool = True,
        remove_call: bool = False,
        interpret_as_response: bool = False,
    ) -> (
        Callable[[Callable[..., JsonType]], Callable[..., JsonType]]
        | Callable[..., JsonType]
    ):
        """Add a function to the functions available to the AI

        Args:
            function (OpenAIFunction | Callable[..., JsonType]): The function to add
            name (str): The name of the function. Defaults to the function's name.
            description (str): The description of the function. Defaults to getting
                the short description from the function's docstring.
            save_return (bool): Whether to send the return value of this function back
                to the AI. Defaults to True.
            serialize (bool): Whether to serialize the return value of this function.
                Otherwise, the return value must be a string.
            remove_call (bool): Whether to remove the function call itself from the chat
                history
            interpret_as_response (bool): Whether to interpret the return value of this
                function as the natural language response of the AI.

        Returns:
            Callable[[Callable[..., JsonType]], Callable[..., JsonType]]: A decorator
            Callable[..., JsonType]: The original function
        """
        if function is None:
            return self.skills.add_function(
                name=name,
                description=description,
                save_return=save_return,
                serialize=serialize,
                remove_call=remove_call,
                interpret_as_response=interpret_as_response,
            )
        return self.skills.add_function(
            function,
            name=name,
            description=description,
            save_return=save_return,
            serialize=serialize,
            remove_call=remove_call,
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

    def ask(self, question: str, retries: int | None = 1) -> str:
        """Ask the AI a question, running until a response is generated

        Args:
            question (str): The question
            retries (int | None): The number of retries; if None, will retry
                indefinitely

        Returns:
            str: The answer to the question
        """
        self.add_message(question)
        return self.run_until_response(retries=retries).content

    def add_skill(self, skill: FunctionSet) -> None:
        """Add a skill to those available to the AI

        Args:
            skill (FunctionSet): The skill to add
        """
        self.skills.add_skill(skill)

    def run(
        self, function: str, prompt: str | None = None, retries: int | None = 1
    ) -> Any:
        """Run a specified function and return the raw function result

        Args:
            function (str): The function to run
            prompt (str | None): The prompt to use
            retries (int | None): The number of retries; if None, will retry
                indefinitely

        Returns:
            The raw function result
        """
        if prompt is not None:
            self.add_message(prompt)
        # We can do type: ignore as we know we're forcing a function call
        response: FunctionCallMessage
        response = self.generate_message(
            {"name": function}, retries=retries
        )  # type: ignore
        return self.skills(response.function_call)
