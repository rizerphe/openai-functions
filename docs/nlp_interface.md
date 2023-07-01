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
    system_prompt="You're an AI capable of changing the weather.",
    model="gpt-4-0613"
)
def set_current_weather(location: str, description: str):
    return "Set the weather successfully"
```

The parameters it takes are:

- `system_prompt` - if provided, when asking the AI, the conversation will start with this system prompt, letting you modify the behavior of the model
- `model` - this is just the model to use; currently (July 1st 2023) only `gpt-3.5-turbo-0613`, `gpt-3.5-turbo-16k-0613` and `gpt-4-0613` are supported

Note: mypy does not parse class decorators ([#3135](https://github.com/python/mypy/issues/3135)), so you might have trouble getting type checking when using it like a decorator for a dataclass.
