# openai interfaces

import openai

from ..default import SYSTEM, OPENAI_MODEL, payload_openai, response_openai, stream_openai

def get_llm_response(prompt, api_key=None, model=OPENAI_MODEL, system=SYSTEM, **kwargs):
    client = openai.OpenAI(api_key=api_key)
    payload = payload_openai(system, prompt)
    response = client.chat.completions.create(model=model, **payload, **kwargs)
    return response_openai(response)

def stream_llm_response(prompt, api_key=None, model=OPENAI_MODEL, system=SYSTEM, **kwargs):
    client = openai.OpenAI(api_key=api_key)
    payload = payload_openai(system, prompt)
    response = client.chat.completions.create(model=model, stream=True, **payload, **kwargs)
    for chunk in response:
        yield stream_openai(chunk)
