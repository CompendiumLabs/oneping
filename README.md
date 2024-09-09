# oneping

>Give me a ping, Vasily. One ping only, please.

![One ping only, please.](oneping.png)

This is a simple wrapper library for querying LLMs via URL or native package. Currently the following providers are supported:

- OpenAI
- Anthropic
- Fireworks
- x.ai (native only)

In addition, you can target local models at `localhost` that use an OpenAI-compatible API such as `llama.cpp` or `llama-cpp-python`. Also included is a simple function to start a `llama-cpp-python` server on the fly (`oneping.server.run_llama_server`).

The various native libraries are soft dependencies and the library can still partially function with or without any or all of them. The native packages for these providers are: `openai`, `anthropic`, `fireworks-ai`, and `xai-sdk`.

## Installation

```bash
pip install oneping
```

## Usage

Basic usage with Anthropic through the URL interface:
```python
response = oneping.get_llm_response(prompt, provider='anthropic')
```

The `get_llm_response` function accepts a number of arguments including:

- `prompt` (required): The prompt to send to the LLM (required)
- `provider` = `local`: The provider to use: `openai`, `anthropic`, `fireworks`, `xai`, or `local`
- `system` = `None`: The system prompt to use (not required, but recommended)
- `prefill` = `None`: Prefill starts the "assistant" response with a string (Anthropic doesn't like newlines in this)
- `history` = `None`: List of prior messages or `True` to request full history as return value.
- `url` = `None`: Override the default URL for the provider.
- `port` = `8000`: Which port to use for local or custom provider.
- `api_key` = `None`: The API key to use for non-local providers.
- `model` = `None`: Indicate the desired model for the provider.
- `max_tokens` = `1024`: The maximum number of tokens to return.
- `stream` = `False`: Whether to stream the response (returns a generator)

For example, to use the OpenAI API with a custom `system` prompt:
```python
response = oneping.get_llm_response(prompt, provider='openai', system=system)
```

To conduct a full conversation with a local LLM:
```python
history = True
history = oneping.get_llm_response(prompt1, provider='local', history=history)
history = oneping.get_llm_response(prompt2, provider='local', history=history)
```

For streaming, either pass `stream=True` or use the `oneping.stream_llm_response` helper function.