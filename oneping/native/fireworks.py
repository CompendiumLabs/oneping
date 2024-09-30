# fireworks interface

import fireworks.client

from ..providers import (
    DEFAULT_SYSTEM, FIREWORKS_MODEL, payload_openai,
    response_openai_native, stream_openai_native
)

def get_llm_response(query, api_key=None, model=FIREWORKS_MODEL, system=DEFAULT_SYSTEM, **kwargs):
    client = fireworks.client.Fireworks(api_key=api_key)
    payload = payload_openai(query, system=system)
    response = client.chat.completions.create(model=model, **payload, **kwargs)
    return response_openai_native(response)

async def async_llm_response(query, api_key=None, model=FIREWORKS_MODEL, system=DEFAULT_SYSTEM, **kwargs):
    client = fireworks.client.Fireworks(api_key=api_key)
    payload = payload_openai(query, system=system)
    response = client.chat.completions.acreate(model=model, stream=True, **payload, **kwargs)
    async for chunk in response:
        yield stream_openai_native(chunk)

def stream_llm_response(query, api_key=None, model=FIREWORKS_MODEL, system=DEFAULT_SYSTEM, **kwargs):
    client = fireworks.client.Fireworks(api_key=api_key)
    payload = payload_openai(query, system=system)
    response = client.chat.completions.create(model=model, stream=True, **payload, **kwargs)
    for chunk in response:
        yield stream_openai_native(chunk)

def embed(text, api_key=None, model=FIREWORKS_MODEL, system=DEFAULT_SYSTEM, **kwargs):
    client = fireworks.client.Fireworks(api_key=api_key)
    payload = payload_openai(text, system=system)
    response = client.embeddings.create(model=model, **payload, **kwargs)
    return response_openai_native(response)
