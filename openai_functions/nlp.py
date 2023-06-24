"""A module for running OpenAI functions"""
from __future__ import annotations
from functools import partial, wraps
from typing import Any, Callable, TYPE_CHECKING, overload

from .conversation import Conversation
from .functions.wrapper import FunctionWrapper


if TYPE_CHECKING:
    from .json_type import JsonType
    from .functions.functions import OpenAIFunction


class Wrapper:
    """A wrapper for a function"""

    def __init__(
        self,
        origin: Callable[..., JsonType],
        system_prompt: str | None = None,
        model: str = "gpt-3.5-turbo-0613",
    ) -> None:
        self.origin = origin
        self.system_prompt = system_prompt
        self.conversation = Conversation(model=model)
        self.openai_function = FunctionWrapper(self.origin)
        self.conversation.add_function(self.openai_function)

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.origin(*args, **kwds)

    def nlp(self, prompt: str) -> Any:
        """Run the function with the given prompt

        Args:
            prompt (str): The prompt to use

        Returns:
            The result of the original function
        """
        self.conversation.clear_messages()
        if self.system_prompt is not None:
            self.conversation.add_message(
                {
                    "role": "system",
                    "content": self.system_prompt,
                }
            )
        return self.conversation.run(self.openai_function.name, prompt)


@overload
def nlp(
    function: Callable[..., JsonType],
    *,
    system_prompt: str | None = None,
    model: str = "gpt-3.5-turbo-0613",
) -> Callable[[str], JsonType]:
    ...


@overload
def nlp(
    *,
    system_prompt: str | None = None,
    model: str = "gpt-3.5-turbo-0613",
) -> Callable[[Callable[..., JsonType] | OpenAIFunction], Callable[[str], JsonType]]:
    ...


def nlp(
    function: Callable[..., JsonType] | None = None,
    *,
    system_prompt: str | None = None,
    model: str = "gpt-3.5-turbo-0613",
) -> (
    Callable[[str], JsonType]
    | Callable[[Callable[..., JsonType]], Callable[[str], JsonType]]
):
    """Add natural language input to a function

    Args:
        function (Callable[..., JsonType] | None): The function
            to add natural language input to
        system_prompt (str | None): The system prompt to use. Defaults to None.
        model (str): The model to use. Defaults to "gpt-3.5-turbo-0613".

    Returns:
        The function, with natural language input, or a decorator to add natural
        language input to a function
    """

    if function is None:
        return partial(nlp, system_prompt=system_prompt, model=model)

    return wraps(function)(Wrapper(function, system_prompt=system_prompt, model=model))
