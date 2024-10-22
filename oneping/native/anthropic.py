# anthropic interface

import anthropic

from ..providers import (
    DEFAULT_SYSTEM, DEFAULT_MAX_TOKENS, ANTHROPIC_MODEL,
    payload_anthropic, response_anthropic_native, stream_anthropic_native
)

def reply(
    query, history=None, prefill=None, system=None, api_key=None, model=None,
    max_tokens=DEFAULT_MAX_TOKENS, **kwargs
):
    # handle unspecified defaults
    system = DEFAULT_SYSTEM if system is None else system
    model = ANTHROPIC_MODEL if model is None else model

    # construct client and payload
    client = anthropic.Anthropic(api_key=api_key)
    payload = payload_anthropic(query, system=system, history=history, prefill=prefill)

    # get response and convert to text
    response = client.messages.create(model=model, max_tokens=max_tokens, **payload, **kwargs)
    text = response_anthropic_native(response)
    return (prefill + text) if prefill is not None else text

async def reply_async(
    query, history=None, prefill=None, system=None, api_key=None, model=None,
    max_tokens=DEFAULT_MAX_TOKENS, **kwargs
):
    # handle unspecified defaults
    system = DEFAULT_SYSTEM if system is None else system
    model = ANTHROPIC_MODEL if model is None else model

    # construct client and payload
    client = anthropic.AsyncAnthropic(api_key=api_key)
    payload = payload_anthropic(query, system=system, history=history, prefill=prefill)

    # get response and convert to text
    response = await client.messages.create(model=model, stream=True, max_tokens=max_tokens, **payload, **kwargs)
    text = response_anthropic_native(response)
    return (prefill + text) if prefill is not None else text

def stream(
    query, history=None, prefill=None, system=None, api_key=None, model=None,
    max_tokens=DEFAULT_MAX_TOKENS, **kwargs
):
    # handle unspecified defaults
    system = DEFAULT_SYSTEM if system is None else system
    model = ANTHROPIC_MODEL if model is None else model

    # construct client and payload
    client = anthropic.Anthropic(api_key=api_key)
    payload = payload_anthropic(query, system=system, history=history, prefill=prefill)

    # yield prefill if any
    if prefill is not None:
        yield prefill

    # stream response
    response = client.messages.create(model=model, stream=True, max_tokens=max_tokens, **payload, **kwargs)
    for chunk in response:
        yield stream_anthropic_native(chunk)

async def stream_async(
    query, history=None, prefill=None, system=None, api_key=None, model=None,
    max_tokens=DEFAULT_MAX_TOKENS, **kwargs
):
    # handle unspecified defaults
    system = DEFAULT_SYSTEM if system is None else system
    model = ANTHROPIC_MODEL if model is None else model

    # construct client and payload
    client = anthropic.AsyncAnthropic(api_key=api_key)
    payload = payload_anthropic(query, system=system, history=history, prefill=prefill)

    # yield prefill if any
    if prefill is not None:
        yield prefill

    # stream response
    response = await client.messages.create(model=model, stream=True, max_tokens=max_tokens, **payload, **kwargs)
    async for chunk in response:
        yield stream_anthropic_native(chunk)
