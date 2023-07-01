# Skills

A skill allows you to combine several functions into one object, generate schemas for all those functions, and then call the function the AI requests. The most basic skill is defined with a [BasicFunctionSet](openai_functions.BasicFunctionSet) - it is just a function container. Here's an example of its usage:

```python
skill = BasicFunctionSet()

@skill.add_function
def get_current_weather(location: str) -> dict:
...

@skill.add_function(
    save_return=True,
    serialize=False,
    interpret_as_response=True
)
def set_weather(location: str, weather_description: str):
   ...

schema = skill.functions_schema
```

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
