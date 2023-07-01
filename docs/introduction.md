# Introduction

The `openai-functions` Python project simplifies the usage of OpenAI's function calling feature. It abstracts away the complexity of parsing function signatures and docstrings by providing developers with a clean and intuitive interface.

`openai-functions` takes care of the following tasks:

- Parsing the function signatures (with type annotations) and docstrings.
- Sending the conversation and function descriptions to the OpenAI model.
- Deciding whether to call a function based on the model's response.
- Calling the appropriate function with the provided arguments.
- Updating the conversation with the function response.
- Repeating the process until the model generates a user-facing message.

This abstraction allows developers to focus on defining their functions and adding user messages without worrying about the details of function calling.

# Quickstart

## Installation

You can install `openai-functions` from PyPI using pip:

```
pip install openai-functions
```

Now, there are **three ways you can use this** - start with just one:

- For managing conversations, use the [conversational](#your-first-conversation) interface
- For data extraction etc., for working with just one function, use the [data extraction](extracting-data) interface
- For just generating schemas and parsing call results, nothing more, use [raw schema generation](just-generating-the-schemas) next.

(your-first-conversation)=
## Your first conversation

The easiest way to use `openai-functions` is through the [conversation](conversation) interface. For that, you first import all of the necessary modules and initialize openai with your API key:

```python
import enum
import openai
from openai_functions import Conversation

openai.api_key = "<YOUR_API_KEY>"
```

Then, we can create a [conversation](openai_functions.Conversation).

```python
conversation = Conversation()
```

A conversation contains our and the AI's messages, the functions we provide, and a set of methods for calling the AI with our functions. Now, we can add our functions to the conversation using the `@conversation.add_function` decorator to make them available for the AI:

```python
class Unit(enum.Enum):
    FAHRENHEIT = "fahrenheit"
    CELSIUS = "celsius"

@conversation.add_function()
def get_current_weather(location: str, unit: Unit = Unit.FAHRENHEIT) -> dict:
    """Get the current weather in a given location.

    Args:
        location (str): The city and state, e.g., San Francisco, CA
        unit (Unit): The unit to use, e.g., fahrenheit or celsius
    """
    return {
        "location": location,
        "temperature": "72",
        "unit": unit.value,
        "forecast": ["sunny", "windy"],
    }
```

Note that the function _must_ have type annotations for all arguments, including extended type annotations for lists/dictionaries (for example, `list[int]` and not just `list`); otherwise the tool won't be able to generate a schema. Our conversation is now ready for function calling. The easiest way to do so is through the `conversation.ask` method. This method will repeatedly ask the AI for a response, running function calls, until the AI responds with text to return:

```python
response = conversation.ask("What's the weather in San Francisco?")
# Should return something like:
# The current weather in San Francisco is 72 degrees Fahrenheit and it is sunny and windy.
```

The AI will probably (nobody can say for sure) then return a function call with the arguments of `{"location": "San Francisco, CA"}`, which will get translated to `get_current_weather("San Francisco, CA")`. The function response will be serialized and sent back to the AI, and the AI will return a text description. You can read more about how to work with conversations [here](conversation).

(extracting-data)=
## Extracting data

There are two common uses for function calls: assistant-type applications, which is what conversations are for, and data extraction, where you force the AI to call a specific function and fill in the arguments. We have the [nlp interface](nlp_interface) for data extraction. It acts as a decorator, turning a function (or a class, including a dataclass) into a [wrapper](openai_functions.Wrapper) object, exposing methods for calling a function with natural language and annotating the call result with an AI response. To use it, you first import all of the necessary modules and initialize openai with your API key:

```python
from dataclasses import dataclass
import openai
from openai_functions import nlp

openai.api_key = "<YOUR_API_KEY>"
```

Then, we define our callable (a function or a class) to call when extracting data:

```python
@nlp
@dataclass
class Person:
    """Extract personal info"""

    name: str
    age: int
```

Note that the callable _must_ have type annotations for all arguments (the arguments of the function itself or of the class constructor), and this includes extended type annotations for lists/dictionaries (for example, `list[int]` and not just `list`), otherwise the tool won't be able to generate a schema. Also, mypy does not parse class decorators ([#3135](https://github.com/python/mypy/issues/3135)), so you might have trouble getting type checking when using it like this. When working with classes, including dataclasses, consider using `nlp(Person)` directly to get proper type support.

This sets `Person` to a [wrapper](openai_functions.Wrapper), which allows us to call `Person.from_natural_language` for data extraction:

```python
person = Person.from_natural_language("I'm Jack and I'm 20 years old.")
# Person(name="Jack", age=20)
# (probably, it's not reproducible with temperature > 0)
```

The tool will call the AI, telling it to call the function `Person`. It will then generate a function call with the arguments of `{"name": "Jack", "age": 20}`, and the tool will parse it and call `Person(name="Jack", age=20)`, returning the result of this call. You can read more about how to work with `@nlp` [here](nlp_interface).

(just-generating-the-schemas)=
## Just generating the schemas

If you want to generate the schemas, you can use a [FunctionWrapper](openai_functions.FunctionWrapper):

```python
from openai_functions import FunctionWrapper

wrapper = FunctionWrapper(get_current_weather)
schema = wrapper.schema
result = wrapper({"location": "San Francisco, CA"})
```

This creates an object that can both return you a schema of a function and provide the function with properly parsed arguments. Another tool is a [FunctionSet](openai_functions.BasicFunctionSet) that allows you to aggregate multiple functions into one schema:

```python
from openai_functions import BasicFunctionSet
import enum

skill = BasicFunctionSet()

class Unit(enum.Enum):
    FAHRENHEIT = "fahrenheit"
    CELSIUS = "celsius"

@skill.add_function
def get_current_weather(location: str, unit: Unit = Unit.FAHRENHEIT) -> dict:
    """Get the current weather in a given location.

    Args:
        location (str): The city and state, e.g., San Francisco, CA
        unit (Unit): The unit to use, e.g., fahrenheit or celsius
    """
    return {
        "location": location,
        "temperature": "72",
        "unit": unit.value,
        "forecast": ["sunny", "windy"],
    }

@skill.add_function
def set_weather(location: str, weather_description: str):
   ...

schema = skill.functions_schema
```

This then generates the schema for your functions.<details><summary>This is what `schema` looks like</summary>

```json
[
  {
    "name": "get_current_weather",
    "parameters": {
      "type": "object",
      "properties": {
        "location": {
          "type": "string",
          "description": "The city and state, e.g., San Francisco, CA"
        },
        "unit": {
          "type": "string",
          "enum": ["FAHRENHEIT", "CELSIUS"],
          "description": "The unit to use, e.g., fahrenheit or celsius"
        }
      },
      "required": ["location"]
    },
    "description": "Get the current weather in a given location."
  },
  {
    "name": "set_weather",
    "parameters": {
      "type": "object",
      "properties": {
        "location": {
          "type": "string"
        },
        "weather_description": {
          "type": "string"
        }
      },
      "required": ["location", "weather_description"]
    }
  }
]
```

</details>

You can now call the functions directly using the function calls OpenAI returns:

```python
weather = skill(
    {"name": "get_current_weather", "arguments": '{"location": "San Francisco, CA"}'}
)
```

This then calls the relevant function.<details><summary>`weather` is then just the raw return value of it, in this case:</summary>

```json
{
  "location": "San Francisco, CA",
  "temperature": "72",
  "unit": "fahrenheit",
  "forecast": ["sunny", "windy"]
}
```

</details>

You can read more about how to work with skills [here](skills).
