# anthropic interface

import os
import anthropic

from ..providers import (
    CONFIG as C, PROVIDERS as P,
    content_anthropic, convert_history, payload_anthropic,
    response_anthropic_native, stream_anthropic_native
)

##
## helper functions
##

def make_payload(query, image=None, system=None, history=None):
    content = content_anthropic(query, image=image)
    history = convert_history(history, content_anthropic)
    return payload_anthropic(content, system=system, history=history)

##
## common interface
##

def make_client(async_client=False, api_key=None):
    api_key = api_key if api_key is not None else os.environ.get(P.anthropic.api_key_env)
    client_class = anthropic.AsyncAnthropic if async_client else anthropic.Anthropic
    return client_class(api_key=api_key, default_headers=P.anthropic.headers)

def reply(query, image=None, history=None, prefill=None, prediction=None, system=C.system, api_key=None, model=P.anthropic.chat_model, max_tokens=C.max_tokens, **kwargs):
    client = make_client(api_key=api_key)
    payload = make_payload(query, image=image, system=system, history=history)
    response = client.messages.create(model=model, max_tokens=max_tokens, **payload, **kwargs)
    return response_anthropic_native(response)

async def reply_async(query, image=None, history=None, prefill=None, prediction=None, system=C.system, api_key=None, model=None, max_tokens=C.max_tokens, **kwargs):
    model = model if model is not None else P.anthropic.chat_model
    client = make_client(async_client=True, api_key=api_key)
    payload = make_payload(query, image=image, system=system, history=history)
    response = await client.messages.create(model=model, max_tokens=max_tokens, **payload, **kwargs)
    text = response_anthropic_native(response)
    return (prefill + text) if prefill is not None else text

def stream(query, image=None, history=None, prefill=None, prediction=None, system=C.system, api_key=None, model=None, max_tokens=C.max_tokens, **kwargs):
    model = model if model is not None else P.anthropic.chat_model
    client = make_client(api_key=api_key)
    payload = make_payload(query, image=image, system=system, history=history)
    response = client.messages.create(model=model, stream=True, max_tokens=max_tokens, **payload, **kwargs)
    if prefill is not None:
        yield prefill
    for chunk in response:
        yield stream_anthropic_native(chunk)

async def stream_async(query, image=None, history=None, prefill=None, prediction=None, system=C.system, api_key=None, model=None, max_tokens=C.max_tokens, **kwargs):
    model = model if model is not None else P.anthropic.chat_model
    client = make_client(async_client=True, api_key=api_key)
    payload = make_payload(query, image=image, system=system, history=history)
    response = await client.messages.create(model=model, stream=True, max_tokens=max_tokens, **payload, **kwargs)
    if prefill is not None:
        yield prefill
    async for chunk in response:
        yield stream_anthropic_native(chunk)
