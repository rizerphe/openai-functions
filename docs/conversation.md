# Conversations

For assistant-type applications, `Conversation` is the most intuitive tool. It allows you to store messages and generate new ones, either by using the AI or by calling a function you provide.

A conversation contains two things:

- the messages in the conversation.
- a skill (composed from a list of [skills](skills) and a list of [`OpenAIFunction`](openai_functions.OpenAIFunction)s inherent to the conversation)

When initializing the conversation, you can pass in the list of skills and the model to use.

## Managing messages

The main feature of a conversation is its management of messages. You can either directly access them with `conversation.messages` (which is a list of objects adhering to the [GenericMessage](openai_functions.GenericMessage) protocol - use [Message](openai_functions.Message) to create your own), or you can do these:

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

A conversation also includes the skills - the functions the AI can call. You can either provide your skills when creating the conversation, or add skills/functions like this:

```python
conversation.add_skill(skill)
conversation.add_function(openai_function)

@conversation.add_function
def my_awesome_function(...):
    ...

@conversation.add_function(
    save_return=True,
    serialize=False,
    interpret_as_response=False
)
def my_amazing_function():
    return ""

conversation.remove_function(openai_function)
conversation.remove_function(my_awesome_function)
conversation.remove_function("my_amazing_function")
```

The arguments passed to `add_function` are the same as those an [OpenAIFunction](openai_functions.OpenAIFunction) inherently has:

- `save_return` - whether to send the return value of the function back to the AI; some functions - mainly those that don't return anything - don't need to do this
- `serialize` - whether to serialize the return value of the function before sending the result back to the AI; openai expects the result of a function call to be a string, so if this is set to False, the result of the function execution should be a string. Otherwise, it will use json serialization, so if `serialize` is set to True, the function return needs to be json-serializable
- `interpret_as_response` - whether to interpret the return value of the function (the serialized one if `serialize` is set to True) as the response from the AI, replacing the function call

You can read more about how to use skills [here](skills).
