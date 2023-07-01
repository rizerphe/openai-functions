# OpenAI functions

The `openai-functions` Python project simplifies the usage of OpenAI's ChatGPT [function calling](https://platform.openai.com/docs/guides/gpt/function-calling) feature. It abstracts away the complexity of parsing function signatures and docstrings by providing developers with a clean and intuitive interface.

![Tests](https://github.com/rizerphe/openai-functions/actions/workflows/tests.yml/badge.svg) [![Coverage Status](https://coveralls.io/repos/github/rizerphe/openai-functions/badge.svg?branch=main)](https://coveralls.io/github/rizerphe/openai-functions?branch=main) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![PyPI version](https://badge.fury.io/py/openai-functions.svg)](https://badge.fury.io/py/openai-functions) [![Documentation Status](https://readthedocs.org/projects/openai-functions/badge/?version=latest)](https://openai-functions.readthedocs.io/en/latest/?badge=latest)

## Installation

You can install `openai-functions` from PyPI using pip:

```
pip install openai-functions
```

## Usage

1. Import the necessary modules and provide your API key:

```python
import enum
import openai
from openai_functions import Conversation

openai.api_key = "<YOUR_API_KEY>"
```

2. Create a `Conversation` instance:

```python
conversation = Conversation()
```

3. Define your functions using the `@conversation.add_function` decorator:

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

4. Ask the AI a question:

```python
response = conversation.ask("What's the weather in San Francisco?")
# Should return something like:
# The current weather in San Francisco is 72 degrees Fahrenheit and it is sunny and windy.
```

You can read more about how to use `Conversation` [here](https://openai-functions.readthedocs.io/en/latest/conversation.html).

## More barebones use - just schema generation and result parsing:

```python
from openai_functions import FunctionWrapper

wrapper = FunctionWrapper(get_current_weather)
schema = wrapper.schema
result = wrapper({"location": "San Francisco, CA"})
```

Or you could use [skills](https://openai-functions.readthedocs.io/en/latest/skills.html).

## Another use case: data extraction

1. Import the necessary modules and provide your API key:

```python
from dataclasses import dataclass
import openai
from openai_functions import nlp

openai.api_key = "<YOUR_API_KEY>"
```

3. Define your data container using the `@nlp` decorator:

```python
@nlp
@dataclass
class Person:
    """Extract personal info"""

    name: str
    age: int
```

4. Ask the AI for the extracted data:

```python
person = Person.from_natural_language("I'm Jack and I'm 20 years old.")
```

You can read more about `@nlp` [here](https://openai-functions.readthedocs.io/en/latest/nlp_interface.html).

Note: mypy does not parse class decorators ([#3135](https://github.com/python/mypy/issues/3135)), so you might have trouble getting type checking when using it like this. Consider using something like `nlp(Person).from_natural_language` to get proper type support.

## How it Works

`openai-functions` takes care of the following tasks:

- Parsing the function signatures (with type annotations) and docstrings.
- Sending the conversation and function descriptions to the OpenAI model.
- Deciding whether to call a function based on the model's response.
- Calling the appropriate function with the provided arguments.
- Updating the conversation with the function response.
- Repeating the process until the model generates a user-facing message.

This abstraction allows developers to focus on defining their functions and adding user messages without worrying about the details of function calling.

## Note

Please note that `openai-functions` is an unofficial project not maintained by OpenAI. Use it at your discretion.
