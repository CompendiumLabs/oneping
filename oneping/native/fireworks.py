# fireworks interface

import fireworks.client

from ..providers import (
    DEFAULT_SYSTEM, FIREWORKS_MODEL, payload_openai,
    response_openai_native, stream_openai_native
)

def reply(query, history=None, system=None, api_key=None, model=None, **kwargs):
    # handle unspecified defaults
    system = DEFAULT_SYSTEM if system is None else system
    model = FIREWORKS_MODEL if model is None else model

    # construct client and payload
    client = fireworks.client.Fireworks(api_key=api_key)
    payload = payload_openai(query, system=system, history=history)

    # get response and convert to text
    response = client.chat.completions.create(model=model, **payload, **kwargs)
    return response_openai_native(response)

async def reply_async(query, history=None, system=None, api_key=None, model=None, **kwargs):
    # handle unspecified defaults
    system = DEFAULT_SYSTEM if system is None else system
    model = FIREWORKS_MODEL if model is None else model

    # construct client and payload
    client = fireworks.client.AsyncFireworks(api_key=api_key)
    payload = payload_openai(query, system=system, history=history)

    # get response and convert to text
    response = await client.chat.completions.acreate(model=model, **payload, **kwargs)
    return response_openai_native(response)

def stream(query, history=None, system=None, api_key=None, model=None, **kwargs):
    # handle unspecified defaults
    system = DEFAULT_SYSTEM if system is None else system
    model = FIREWORKS_MODEL if model is None else model

    # construct client and payload
    client = fireworks.client.Fireworks(api_key=api_key)
    payload = payload_openai(query, system=system, history=history)

    # stream response
    response = client.chat.completions.create(model=model, stream=True, **payload, **kwargs)
    for chunk in response:
        yield stream_openai_native(chunk)

async def stream_async(query, history=None, system=None, api_key=None, model=None, **kwargs):
    # handle unspecified defaults
    system = DEFAULT_SYSTEM if system is None else system
    model = FIREWORKS_MODEL if model is None else model

    # construct client and payload
    client = fireworks.client.AsyncFireworks(api_key=api_key)
    payload = payload_openai(query, system=system, history=history)

    # stream response
    response = await client.chat.completions.acreate(model=model, stream=True, **payload, **kwargs)
    async for chunk in response:
        yield stream_openai_native(chunk)
