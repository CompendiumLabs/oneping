# anthropic interface

import anthropic

from ..default import (
    SYSTEM, ANTHROPIC_MODEL, syncify, payload_anthropic,
    response_anthropic_native, stream_anthropic_native
)

def get_llm_response(prompt, api_key=None, model=ANTHROPIC_MODEL, system=SYSTEM, max_tokens=1024, **kwargs):
    client = anthropic.Anthropic(api_key=api_key)
    payload = payload_anthropic(prompt, system=system)
    response = client.messages.create(model=model, max_tokens=max_tokens, **payload, **kwargs)
    return response_anthropic_native(response)

async def async_llm_response(prompt, api_key=None, model=ANTHROPIC_MODEL, system=SYSTEM, max_tokens=1024, **kwargs):
    client = anthropic.AsyncAnthropic(api_key=api_key)
    payload = payload_anthropic(prompt, system=system)
    response = await client.messages.create(model=model, stream=True, max_tokens=max_tokens, **payload, **kwargs)
    async for chunk in response:
        yield stream_anthropic_native(chunk)

def stream_llm_response(prompt, **kwargs):
    response = async_llm_response(prompt, **kwargs)
    return syncify(response)
