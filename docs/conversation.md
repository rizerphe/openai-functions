# Conversations

For assistant-type applications, `Conversation` is the most intuitive tool. It allows you to store messages and generate new ones using AI or calling a function you provide.

A conversation contains two things:

- the messages in the conversation.
- a skill (composed from a list of [skills](skills) and a list of [`OpenAIFunction`](openai_functions.OpenAIFunction)s inherent to the conversation)

When initializing the conversation, you can pass in the list of skills and the model to use.

## Managing messages

The main feature of a conversation is its management of messages. You can either use `conversation.messages` (which is a list of objects adhering to the [GenericMessage](openai_functions.GenericMessage) protocol - use [Message](openai_functions.Message) to create your own) to directly access them or you can use these:

```python
conversation.add_message(Message("Hi there", role="user"))  # "system", "user", "assistant"
conversation.add_message({
    "role": "assistant",
    "content": "Hello! How can I assist you today?"
})  # Will be converted to a Message object automatically
conversation.add_message('Say "no"')  # Will be turned into a user message by default
conversation.add_messages([Message("No.", "assistant"), "Oh ok"])  # Adding several at once
conversation.pop_message(0)  # Delete the first one
conversation.clear_messages()
```

## Managing skills

A conversation also includes the skills - the functions the AI can call. You can either provide your skills when creating the conversation or add skills/functions like this:

```python
conversation.add_skill(skill)
conversation.add_function(openai_function)

@conversation.add_function
def my_awesome_function(...):
    ...

@conversation.add_function(
    name="my_really_amazing_function",
    description="The most amazing function of them all",
    save_return=True,
    serialize=False,
    remove_call=False,
    interpret_as_response=False
)
def my_amazing_function():
    return ""

conversation.remove_function(openai_function)
conversation.remove_function(my_awesome_function)
conversation.remove_function("my_amazing_function")
```

All of the keyword arguments passed to `add_function` are optional; most of them are the same as those an [OpenAIFunction](openai_functions.OpenAIFunction) inherently has:

- `name` - the overwritten function name, otherwise will default to the function name
- `description` - the overwritten function description sent to the AI - will use the description from the docstring by default
- `save_return` - whether to send the return value of the function back to the AI; some functions - mainly those that don't return anything - don't need to do this
- `serialize` - whether to serialize the function's return value before sending the result back to the AI; openai expects a function call to be a string; if this is False, `str()` will run on the function return. Otherwise, it will use JSON serialization, so if `serialize` is set to True, the function return needs to be JSON-serializable
- `remove_call` - whether to remove the function call message itself; be careful to avoid infinite loops when using with `save_return=False`; the function should then, for example, disappear from the schema; it's your responsibility to make sure this happens
- `interpret_as_response` - whether to interpret the return value of the function (the serialized one if `serialize` is set to True) as the response from the AI

You can read more about how to use skills [here](skills).

## Generating messages

The point of a conversation is to use the AI to generate responses. The easiest way to do this is through the `ask` method:

```python
response = conversation.ask("Your input data")
```

The tool will then repeatedly get responses from OpenAI and run your functions until a full response is generated. Alternatively, if you don't want to add another message to the conversation, you can use the `run_until_response` method that returns a [FinalResponseMessage](openai_functions.FinalResponseMessage) object:

```python
generated_message = conversation.run_until_response()
further_comment = conversation.run_until_response(allow_function_calls=False)
```

If you want to use the conversation to run a specific function more directly and get the execution result, you can use the `run` method, optionally also providing another message:

```python
raw_weather_result = conversation.run("get_weather", "What's the weather in San Francisco?")
```

However, for most usecases [@nlp](nlp_interface) should be sufficient; consider using it.
