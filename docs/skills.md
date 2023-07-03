# Skills

A skill allows you to combine several functions into one object, generate schemas for all those functions, and then call the function the AI requests. The most basic skill is defined with a [BasicFunctionSet](openai_functions.BasicFunctionSet) - it is just a function container. Here's an example of its usage:

```python
skill = BasicFunctionSet()

@skill.add_function
def get_current_weather(location: str) -> dict:
...

@skill.add_function(
    name="set_weather_but_for_real",
    description="Set the weather or something",
    save_return=True,
    serialize=False,
    remove_call=False,
    interpret_as_response=True
)
def set_weather(location: str, weather_description: str):
   ...

schema = skill.functions_schema
```

The parameters here are:

- `name` - the name of the function sent to the AI, defaulting to the function name itself
- `description` - the description of the function sent to the AI, defaults to getting the short description from the function's docstring
- `save_return` - whether to send the return value of the function back to the AI; some functions - mainly those that don't return anything - don't need to do this
- `serialize` - whether to serialize the function's return value before sending the result back to the AI; openai expects a function call to be a string, so if this is False, the result of the function execution should be a string. Otherwise, it will use JSON serialization, so if `serialize` is set to True, the function return needs to be JSON-serializable
- `remove_call` - whether to remove the function call message itself; be careful to avoid infinite loops when using with `save_return=False`; the function should then, for example, disappear from the schema; it's your responsibility to make sure this happens
- `interpret_as_response` - whether to interpret the return value of the function (the serialized one if `serialize` is set to True) as the response from the AI

`schema` will be a list of JSON objects ready to be sent to OpenAI. You can then call your functions directly with the response returned from OpenAI:

```python
weather = skill(
    {"name": "get_current_weather", "arguments": '{"location": "San Francisco, CA"}'}
)
```

## Union skills

A more advanced one is a [union skillset](openai_functions.UnionSkillSet) that combines others. It exposes one new method:

```python
union_skill.add_skill(skill)
```

It still supports everything a [BasicFunctionSet](openai_functions.BasicFunctionSet), though; it can have a few functions inherent to it while still combining the other skillsets.

## Developing your own

Skills are extensible; you can build your own by inheriting them from the [FunctionSet](openai_functions.FunctionSet) base class. You then have to provide these methods and properties:

- `functions_schema` - the schema of the functions; list of JSON objects
- `run_function(input_data)` - that runs the function and returns the result; takes in the raw dictionary retrieved from OpenAI. Should raise [FunctionNotFoundError](openai_functions.FunctionNotFoundError) if there isn't a function with this name in the skillset

You can also inherit from the [MutableFunctionSet](openai_functions.MutableFunctionSet), which greatly simplifies adding and removing functions from the skill. Then, you have to define two additional methods:

- `_add_function(function)` - adds an [OpenAIFunction](openai_functions.OpenAIFunction) to the skill
- `_remove_function(name)` - takes in a string and deletes the function with that name

Your skill will then have the `@skill.add_function` decorator available.
