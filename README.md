# oneping

```python
oneping.reply('Give me a ping, Vasily. One ping only, please.', provider='anthropic')
```

![One ping only, please.](demo/oneping.png)

This is a Python library for querying LLM providers such as OpenAI or Anthropic, as well as local models. The main goal is to create an abstraction layer that makes switching between them seamless. Currently the following providers are supported: `openai`, `anthropic`, `fireworks`, and `local` (local models).

There is also a `Chat` interface that automatically tracks the message history. Kind of departing from the "one ping" notion, but oh well. Additionally, there is a `textual` powered console interface and a `fasthtml` powered web interface. Both are components that can be embedded in other applications.

Requesting the `local` provider will target `localhost` and use an OpenAI-compatible API as in `llama.cpp` or `llama-cpp-python`. The various native libraries are soft dependencies and the library can still partially function with or without any or all of them. The native packages for these providers are: `openai`, `anthropic`, and `fireworks-ai`.

## Installation

For standard usage, install with:

```bash
pip install oneping
```

To install the native provider dependencies add `"[native]"` after `oneping` in the command above. The same goes for the chat interface dependencies with `"[chat]"`.

The easiest way to handle authentication is to set an API key environment variable such as: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `FIREWORKS_API_KEY`, etc. You can also pass the `api_key` argument to any of the functions directly.

## Library Usage

Basic usage with Anthropic through the URL interface:
```python
response = oneping.reply(query, provider='anthropic')
```

The `reply` function accepts a number of arguments including (some of these have per-provider defaults):

- `query` (required): The query to send to the LLM (required)
- `provider` = `local`: The provider to use: `openai`, `anthropic`, `fireworks`, or `local`
- `system` = `None`: The system prompt to use (not required, but recommended)
- `prefill` = `None`: Start "assistant" response with a string (Anthropic doesn't like newlines in this)
- `model` = `None`: Indicate the desired model for the provider (provider default)
- `max_tokens` = `1024`: The maximum number of tokens to return
- `history` = `None`: List of prior messages or `True` to request full history as return value
- `native` = `False`: Use the native provider libraries
- `url` = `None`: Override the default URL for the provider (provider default)
- `port` = `8000`: Which port to use for local or custom provider
- `api_key` = `None`: The API key to use for non-local providers

For example, to use the OpenAI API with a custom `system` prompt:
```python
response = oneping.reply(query, provider='openai', system=system)
```

To conduct a full conversation with a local LLM, see `Chat` interface below. For streaming, use the function `stream` and for `async` streaming, use `stream_async`. Both of these take the same arguments as `reply`.

## Command Line

You can call `oneping` directly or as a module with `python -m oneping` and use the following subcommands:

- `reply`: get a single response from the LLM
- `stream`: stream a response from the LLM
- `embed`: get embeddings from the LLM
- `console`: start a console (Textual) chat
- `web`: start a web (FastHTML) chat

These accept the arguments listed above for `reply` as command line arguments. For example:

```bash
oneping stream "Does Jupiter have a solid core?" --provider anthropic
```

Or you can pipe in your query from `stdin`:

```bash
echo "Does Jupiter have a solid core?" | oneping stream --provider anthropic
```

I've personally found it useful to set up aliases like `claude = oneping stream --provider anthropic`.

## Chat Interface

The `Chat` interface is a simple wrapper for a conversation history. It can be used to chat with an LLM provider or to simply maintain a conversation history for your bot. If takes the usual `reply`, `stream`, and `stream_async` functions, and calling it directly will map to `reply`.

```python
chat = oneping.Chat(provider='anthropic', system=system)
reply1 = chat(query1)
reply2 = chat(query2)
```

There is also a `textual` powered console interface and a `fasthtml` powered web interface. You can call these with: `oneping console` or `oneping web`.

<p align="center">
<img src="demo/textual.png" alt="Textual Chat" width="49%">
<img src="demo/fasthtml.png" alt="FastHTML Chat" width="49%">
</p>

## Server

The `server` module includes a simple function to start a `llama-cpp-python` server on the fly (`oneping.server.start` in Python or `oneping server` from the command line).

```bash
oneping server <path-to-gguf>
```

To run the server in embedding mode, pass the `--embedding` flag. You can also specify things like `--host` and `--port` or any options supported by `llama-cpp-python`.

## Embeddings

Embeddings queries are supported through the `embed` function. It accepts the relevant arguments from the `reply` function. Right now only `openai` and `local` providers are supported.

```python
vecs = oneping.embed(text, provider='openai')
```

and on the command line:

```bash
oneping embed "hello world" --provider openai
```
