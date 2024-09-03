# anthropic interface

import anthropic

from ..default import SYSTEM, ANTHROPIC_MODEL, payload_anthropic, response_anthropic

def get_llm_response(prompt, api_key=None, model=ANTHROPIC_MODEL, system=SYSTEM, **kwargs):
    client = anthropic.Anthropic(api_key=api_key)
    payload = payload_anthropic(system, prompt)
    response = client.messages.create(model=model, **payload, **kwargs)
    return response_anthropic(response)

def stream_llm_response(prompt, api_key=None, model=ANTHROPIC_MODEL, system=SYSTEM, **kwargs):
    client = anthropic.Anthropic(api_key=api_key)
    payload = payload_anthropic(system, prompt)
    with client.messages.create(model=model, stream=True, **payload, **kwargs) as stream:
        for text in stream.text_stream:
            yield text
