# groq interfaces

import groq

from ..default import (
    SYSTEM, GROQ_MODEL, syncify, payload_openai,
    response_openai_native, stream_openai_native
)

def get_llm_response(prompt, api_key=None, model=GROQ_MODEL, system=SYSTEM, **kwargs):
    client = groq.Groq(api_key=api_key)
    payload = payload_openai(prompt, system=system)
    response = client.chat.completions.create(model=model, **payload, **kwargs)
    return response_openai_native(response)

async def async_llm_response(prompt, api_key=None, model=GROQ_MODEL, system=SYSTEM, **kwargs):
    client = groq.AsyncGroq(api_key=api_key)
    payload = payload_openai(prompt, system=system)
    response = await client.chat.completions.create(model=model, stream=True, **payload, **kwargs)
    async for chunk in response:
        yield stream_openai_native(chunk)

def stream_llm_response(prompt, **kwargs):
    response = async_llm_response(prompt, **kwargs)
    return syncify(response)