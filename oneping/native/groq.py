# groq interfaces

import groq

from ..providers import (
    DEFAULT_SYSTEM, GROQ_MODEL, payload_openai,
    response_openai_native, stream_openai_native
)

def get_llm_response(query, api_key=None, model=GROQ_MODEL, system=DEFAULT_SYSTEM, **kwargs):
    client = groq.Groq(api_key=api_key)
    payload = payload_openai(query, system=system)
    response = client.chat.completions.create(model=model, **payload, **kwargs)
    return response_openai_native(response)

async def async_llm_response(query, api_key=None, model=GROQ_MODEL, system=DEFAULT_SYSTEM, **kwargs):
    client = groq.AsyncGroq(api_key=api_key)
    payload = payload_openai(query, system=system)
    response = await client.chat.completions.create(model=model, stream=True, **payload, **kwargs)
    async for chunk in response:
        yield stream_openai_native(chunk)

def stream_llm_response(query, api_key=None, model=GROQ_MODEL, system=DEFAULT_SYSTEM, **kwargs):
    client = groq.Groq(api_key=api_key)
    payload = payload_openai(query, system=system)
    response = client.chat.completions.create(model=model, stream=True, **payload, **kwargs)
    for chunk in response:
        yield stream_openai_native(chunk)

def embed(text, api_key=None, model=GROQ_MODEL, system=DEFAULT_SYSTEM, **kwargs):
    client = groq.Groq(api_key=api_key)
    payload = payload_openai(text, system=system)
    response = client.embeddings.create(model=model, **payload, **kwargs)
    return response_openai_native(response)
