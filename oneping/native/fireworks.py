# fireworks interface

import os
import fireworks.client

from ..providers import (
    DEFAULT_SYSTEM, FIREWORKS_MODEL, FIREWORKS_KEYENV,
    payload_openai, response_openai_native, stream_openai_native
)

def make_client(api_key=None, async_client=False):
    api_key = api_key if api_key is not None else os.environ.get(FIREWORKS_KEYENV)
    client_class = fireworks.client.AsyncFireworks if async_client else fireworks.client.Fireworks
    return client_class(api_key=api_key)

def reply(query, history=None, system=DEFAULT_SYSTEM, api_key=None, model=FIREWORKS_MODEL, **kwargs):
    client = make_client(api_key=api_key)
    payload = payload_openai(query, system=system, history=history)
    response = client.chat.completions.create(model=model, **payload, **kwargs)
    return response_openai_native(response)

async def reply_async(query, history=None, system=DEFAULT_SYSTEM, api_key=None, model=FIREWORKS_MODEL, **kwargs):
    client = make_client(api_key=api_key, async_client=True)
    payload = payload_openai(query, system=system, history=history)
    response = await client.chat.completions.acreate(model=model, **payload, **kwargs)
    return response_openai_native(response)

def stream(query, history=None, system=DEFAULT_SYSTEM, api_key=None, model=FIREWORKS_MODEL, **kwargs):
    client = make_client(api_key=api_key)
    payload = payload_openai(query, system=system, history=history)
    response = client.chat.completions.create(model=model, stream=True, **payload, **kwargs)
    for chunk in response:
        yield stream_openai_native(chunk)

async def stream_async(query, history=None, system=DEFAULT_SYSTEM, api_key=None, model=FIREWORKS_MODEL, **kwargs):
    client = make_client(api_key=api_key, async_client=True)
    payload = payload_openai(query, system=system, history=history)
    response = await client.chat.completions.acreate(model=model, stream=True, **payload, **kwargs)
    async for chunk in response:
        yield stream_openai_native(chunk)
