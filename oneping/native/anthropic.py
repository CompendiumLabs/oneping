# anthropic interface

import os
import anthropic

from ..providers import (
    DEFAULT_SYSTEM, DEFAULT_MAX_TOKENS, ANTHROPIC_MODEL, ANTHROPIC_HEADERS, ANTHROPIC_KEYENV,
    payload_anthropic, response_anthropic_native, stream_anthropic_native
)

def make_client(api_key=None, headers=ANTHROPIC_HEADERS, async_client=False):
    api_key = api_key if api_key is not None else os.environ.get(ANTHROPIC_KEYENV)
    client_class = anthropic.AsyncAnthropic if async_client else anthropic.Anthropic
    return client_class(api_key=api_key, default_headers=headers)

def reply(
    query, history=None, prefill=None, system=DEFAULT_SYSTEM, api_key=None, model=ANTHROPIC_MODEL,
    max_tokens=DEFAULT_MAX_TOKENS, headers=ANTHROPIC_HEADERS, **kwargs
):
    client = make_client(api_key=api_key, headers=headers)
    payload = payload_anthropic(query, system=system, history=history, prefill=prefill)
    response = client.messages.create(model=model, max_tokens=max_tokens, **payload, **kwargs)
    return response_anthropic_native(response)

async def reply_async(
    query, history=None, prefill=None, system=DEFAULT_SYSTEM, api_key=None, model=ANTHROPIC_MODEL,
    max_tokens=DEFAULT_MAX_TOKENS, headers=ANTHROPIC_HEADERS, **kwargs
):
    client = make_client(api_key=api_key, headers=headers, async_client=True)
    payload = payload_anthropic(query, system=system, history=history, prefill=prefill)
    response = await client.messages.create(model=model, max_tokens=max_tokens, **payload, **kwargs)
    text = response_anthropic_native(response)
    return (prefill + text) if prefill is not None else text

def stream(
    query, history=None, prefill=None, system=DEFAULT_SYSTEM, api_key=None, model=ANTHROPIC_MODEL,
    max_tokens=DEFAULT_MAX_TOKENS, headers=ANTHROPIC_HEADERS, **kwargs
):
    client = make_client(api_key=api_key, headers=headers)
    payload = payload_anthropic(query, system=system, history=history, prefill=prefill)
    response = client.messages.create(model=model, stream=True, max_tokens=max_tokens, **payload, **kwargs)
    if prefill is not None:
        yield prefill
    for chunk in response:
        yield stream_anthropic_native(chunk)

async def stream_async(
    query, history=None, prefill=None, system=DEFAULT_SYSTEM, api_key=None, model=ANTHROPIC_MODEL,
    max_tokens=DEFAULT_MAX_TOKENS, headers=ANTHROPIC_HEADERS, **kwargs
):
    client = make_client(api_key=api_key, headers=headers, async_client=True)
    payload = payload_anthropic(query, system=system, history=history, prefill=prefill)
    response = await client.messages.create(model=model, stream=True, max_tokens=max_tokens, **payload, **kwargs)
    if prefill is not None:
        yield prefill
    async for chunk in response:
        yield stream_anthropic_native(chunk)
