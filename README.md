# OpenAI functions

The `openai-functions` Python project simplifies the usage of OpenAI's function calling feature. It abstracts away the complexity of parsing function signatures and docstrings by providing developers with a clean and intuitive interface.

![Tests](https://github.com/rizerphe/openai-functions/actions/workflows/tests.yml/badge.svg) [![Coverage Status](https://coveralls.io/repos/github/rizerphe/openai-functions/badge.svg?branch=main)](https://coveralls.io/github/rizerphe/openai-functions?branch=main)

## Installation

You can install `openai-functions` from PyPI using pip:

```
pip install openai-functions
```

## Usage

1. Import the necessary modules:

```python
import enum
import openai
from openai_functions import Conversation
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
    """
    Get the current weather in a given location.

    Args:
        location (str): The city and state, e.g., San Francisco, CA
        unit (Unit): The unit to use, e.g. fahrenheit or celsius

    Returns:
        dict: A dictionary containing the current weather
    """
    weather_info = {
        "location": location,
        "temperature": "72",
        "unit": unit.value,
        "forecast": ["sunny", "windy"],
    }
    return weather_info
```

4. Ask the AI a question:

```python
conversation.ask("What's the weather in San Francisco?")
```

## Another usecase: data extraction

1. Import the necessary modules:

```python
from dataclasses import dataclass
import openai
from openai_functions import nlp
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

4. Ask the AI for a summary of the data:

```python
Person.nlp("I'm Jack and I'm 20 years old.", "Person")
```

## How it Works

`openai-functions` takes care of the following tasks:

- Parsing the function signatures and docstrings.
- Sending the conversation and function descriptions to the OpenAI model.
- Deciding whether to call a function based on the model's response.
- Calling the appropriate function with the provided arguments.
- Updating the conversation with the function response.
- Repeating the process until the model generates a user-facing message.

This abstraction allows developers to focus on defining their functions and adding user messages without worrying about the details of function calling.

## Note

Please note that `openai-functions` is an unofficial project not maintained by OpenAI. Use it at your discretion.
