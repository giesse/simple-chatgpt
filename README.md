# Simple ChatGPT

Simple ChatGPT is a Python script that allows you to have a conversation with OpenAI's GPT models. It uses OpenAI's GPT models to produce responses given a prompt from the user, allowing for a somewhat natural conversation.

## Prerequisites

First, you'll need to create an OpenAI API key. Instructions can be found [here](https://platform.openai.com/account/api-keys).

To use this script, you will need to have the `openai` module installed. You can install it using `pip`:

```
pip install openai
```

You will also need the `toml` and `pyyaml` modules installed:

```
pip install toml pyyaml
```

## Configuration

To use this script, you'll need to create a `config.toml` file with your OpenAI API key, as well as a system message to display at the beginning of each conversation.

Here's an example `config.toml` file:

```
[openai]
api_key = "YOUR_API_KEY_HERE"
system_message = "You are a helpful assistant."
```

## Usage

To start a conversation, run the following command:

```
python chatgpt.py
```

This will start a new conversation, prompting the user to enter messages.

You can also resume a previous conversation, by specifying the conversation file:

```
python chatgpt.py --conversation conversations/my-conversation.yaml
```

The conversation will be saved to a YAML file in the `conversations` directory. To save the conversation and exit, type `/quit` at the prompt.

## License

This code is released under the [MIT License](LICENSE).
