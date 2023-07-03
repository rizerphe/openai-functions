# @nlp

[nlp](openai_functions.nlp) allows you to convert any callable (works pretty well with dataclasses) that takes in annotated arguments and returns a [Wrapper](openai_functions.Wrapper) around them. This allows you to:

- Call a function or initialize an object:

```python
return_value = nlp(callable).from_natural_language("Your natural language input")
```

- Get a natural language response for the functions that return JSON-serializable output:

```python
response = nlp(callable).natural_language_response("Your natural language input")
```

- For JSON-serializable functions, annotate responses to natural language prompts with natural language responses (returns a [NaturalLanguageAnnotated](openai_functions.NaturalLanguageAnnotated) object):

```python
annotated = nlp(callable).natural_language_annotated("Your natural language input")
natural_language_response = annotated.annotation
raw_function_result = annotated.function_result
```

`@nlp` was designed to be used as a decorator:

```python
@nlp
def get_current_weather(location: str):
    ...

@nlp(
    name="set_current_weather",
    description="Set the current weather for a given location",
    serialize=False,
    system_prompt="You're an AI capable of changing the weather.",
    model="gpt-4-0613"
)
def set_current_weather(location: str, description: str):
    return "Set the weather successfully"
```

Note: watch out for incomplete or invalid responses from OpenAI - currently they do not bother with validating the outputs, and the generation might cut off in the middle of the JSON output. If either of these happens, the tool will raise either [BrokenSchemaError](openai_functions.BrokenSchemaError) or [InvalidJsonError](openai_functions.InvalidJsonError).

The parameters `@nlp` takes are:

- `name` - the name of the function sent to the AI, defaulting to the function name itself
- `description` - the description of the function sent to the AI, defaults to getting the short description from the function's docstring
- `serialize` - whether to serialize the function's return value before sending the result back to the AI; openai expects a function call to be a string, so if this is False, the result of the function execution should be a string. Otherwise, it will use JSON serialization, so if `serialize` is set to True, the function return needs to be JSON-serializable
- `save_return` - whether to send the return value of the function back to the AI; some functions - mainly those that don't return anything - don't need to do this
- `system_prompt` - if provided, when asking the AI, the conversation will start with this system prompt, letting you modify the behavior of the model
- `model` - this is just the model to use; currently (July 1st 2023) only `gpt-3.5-turbo-0613`, `gpt-3.5-turbo-16k-0613` and `gpt-4-0613` are supported

Note: mypy does not parse class decorators ([#3135](https://github.com/python/mypy/issues/3135)), so you might have trouble getting type checking when using it like a decorator for a dataclass.
