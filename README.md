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
from openai_functions import Runner
```

2. Create a `Runner` instance:

```python
runner = Runner()
```

3. Define your functions using the `@runner.add_function` decorator:

```python
class Unit(enum.Enum):
    FAHRENHEIT = "fahrenheit"
    CELSIUS = "celsius"

@runner.add_function
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

4. Add user messages using the `runner.add_message` method:

```python
runner.add_message(
    {
        "role": "user",
        "content": "What's the weather in San Francisco?",
    }
)
```

5. Call the `runner.run_until_response()` method to trigger the conversation and retrieve the response:

```python
print(runner.run_until_response())
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
