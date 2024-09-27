# openai interfaces

import openai

from ..providers import (
    DEFAULT_SYSTEM, OPENAI_MODEL, payload_openai,
    response_openai_native, stream_openai_native
)

def get_llm_response(prompt, api_key=None, model=OPENAI_MODEL, system=DEFAULT_SYSTEM, **kwargs):
    client = openai.OpenAI(api_key=api_key)
    payload = payload_openai(prompt, system=system)
    response = client.chat.completions.create(model=model, **payload, **kwargs)
    return response_openai_native(response)

async def async_llm_response(prompt, api_key=None, model=OPENAI_MODEL, system=DEFAULT_SYSTEM, **kwargs):
    client = openai.AsyncOpenAI(api_key=api_key)
    payload = payload_openai(prompt, system=system)
    response = await client.chat.completions.create(model=model, stream=True, **payload, **kwargs)
    async for chunk in response:
        yield stream_openai_native(chunk)

def stream_llm_response(prompt, api_key=None, model=OPENAI_MODEL, system=DEFAULT_SYSTEM, **kwargs):
    client = openai.OpenAI(api_key=api_key)
    payload = payload_openai(prompt, system=system)
    response = client.chat.completions.create(model=model, stream=True, **payload, **kwargs)
    for chunk in response:
        yield stream_openai_native(chunk)

def get_embed_response(text, api_key=None, model=OPENAI_MODEL, **kwargs):
    client = openai.OpenAI(api_key=api_key)
    response = client.embeddings.create(model=model, input=text, **kwargs)
    return response
