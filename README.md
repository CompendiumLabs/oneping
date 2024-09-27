# oneping

>Give me a ping, Vasily. One ping only, please.

![One ping only, please.](demo/oneping.png)

This is a library for querying LLM providers such as OpenAI or Anthropic, as well as local models. Currently the following providers are supported: `openai`, `anthropic`, `fireworks`, and `local` (local models).

Requesting a `local` provider will target `localhost` and use an OpenAI-compatible API as in `llama.cpp` or `llama-cpp-python`. Also included is a simple function to start a `llama-cpp-python` server on the fly (see below).

The various native libraries are soft dependencies and the library can still partially function with or without any or all of them. The native packages for these providers are: `openai`, `anthropic`, and `fireworks-ai`.

There is also a `Chat` interface that automatically tracks message history. Kind of departing from the "one ping" notion, but oh well. This accepts a `provider` and `system` argument. Other parameters are passed by calling it (an alias for `chat`) or to `stream`.

## Installation

For standard usage, install with:

```bash
pip install oneping
```

To include the native provider dependencies, install with:

```bash
pip install oneping[native]
```

To include the chat and web interface dependencies, install with:

```bash
pip install oneping[chat]
```

## Library Usage

Basic usage with Anthropic through the URL interface:
```python
response = oneping.reply(prompt, provider='anthropic')
```

The `reply` function accepts a number of arguments including (some of these have per-provider defaults):

- `prompt` (required): The prompt to send to the LLM (required)
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
response = oneping.reply(prompt, provider='openai', system=system)
```

To conduct a full conversation with a local LLM:
```python
history = True
history = oneping.reply(prompt1, provider='local', history=history)
history = oneping.reply(prompt2, provider='local', history=history)
```

For streaming, use the function `stream` and for `async` streaming, use `stream_async`. Both of these take the same arguments as `reply`.

## Command Line

You can call the `oneping` module directly and use the following subcommands:

- `reply`: get a single response from the LLM
- `stream`: stream a response from the LLM
- `embed`: get embeddings from the LLM
- `console`: start a console (Textual) chat
- `web`: start a web (FastHTML) chat

These accept the arguments listed above for `reply` as command line arguments. For example:

```bash
python -m oneping stream "Does Jupiter have a solid core?" --provider anthropic
```

Or you can pipe in your query from `stdin`:

```bash
echo "Does Jupiter have a solid core?" | python -m oneping stream --provider anthropic
```

## Chat Interface

The `Chat` interface is a simple wrapper for a conversation history. It can be used to chat with an LLM provider or to simply maintain a conversation history for your bot. If takes the usual `reply`, `stream`, and `stream_async` functions, and calling it directly will map to `reply`.

```python
chat = oneping.Chat(provider='anthropic', system=system)
response1 = chat(prompt1)
response2 = chat(prompt2)
```

There is also a `textual` powered console interface and a `fasthtml` powered web interface. You can call these with: `python -m oneping console` or `python -m oneping web`.

<p align="center">
<img src="demo/textual.png" alt="Textual Chat" width="49%">
<img src="demo/fasthtml.png" alt="FastHTML Chat" width="49%">
</p>

## Server

The `server` module includes a simple function to start a `llama-cpp-python` server on the fly (`oneping.server.start` or `python -m oneping.server start`).

```bash
python -m oneping.server start <path-to-gguf>
```

To run the server in embedding mode, either pass the `--embedding` flag.

## Embeddings

Embeddings queries are supported through the `embed` function. It accepts the relevant arguments from the `reply` function. Right now only `openai` and `local` providers are supported.

```python
vecs = oneping.embed(text, provider='openai')
```
