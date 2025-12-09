# openai interfaces

import os
import openai

from ..providers import (
    CONFIG as C, PROVIDERS as P,
    content_openai, convert_history, payload_openai,
    response_openai_native, stream_openai_native,
    embed_response_openai_native, transcribe_response_openai
)

##
## helper functions
##

def make_payload(query, image=None, prediction=None, system=None, history=None):
    content = content_openai(query, image=image)
    history = convert_history(history, content_openai)
    return payload_openai(content, prediction=prediction, system=system, history=history)

##
## common interface
##

def make_client(async_client=False, base_url=None, api_key=None):
    api_key = api_key if api_key is not None else os.environ.get(P.openai.api_key_env)
    client_class = openai.AsyncOpenAI if async_client else openai.OpenAI
    return client_class(api_key=api_key, base_url=base_url)

def reply(query, image=None, history=None, prefill=None, prediction=None, system=C.system, api_key=None, model=P.openai.chat_model, max_tokens=None, base_url=None, **kwargs):
    client = make_client(base_url=base_url, api_key=api_key)
    payload = make_payload(query, image=image, prediction=prediction, system=system, history=history)
    response = client.chat.completions.create(model=model, max_completion_tokens=max_tokens, **payload, **kwargs)
    return response_openai_native(response)

async def reply_async(query, image=None, history=None, prefill=None, prediction=None, system=C.system, api_key=None, model=P.openai.chat_model, max_tokens=None, base_url=None, **kwargs):
    client = make_client(async_client=True, base_url=base_url, api_key=api_key)
    payload = make_payload(query, image=image, prediction=prediction, system=system, history=history)
    response = await client.chat.completions.create(model=model, max_completion_tokens=max_tokens, **payload, **kwargs)
    return response_openai_native(response)

def stream(query, image=None, history=None, prefill=None, prediction=None, system=C.system, api_key=None, model=P.openai.chat_model, max_tokens=None, base_url=None, **kwargs):
    client = make_client(base_url=base_url, api_key=api_key)
    payload = make_payload(query, image=image, prediction=prediction, system=system, history=history)
    response = client.chat.completions.create(model=model, stream=True, max_completion_tokens=max_tokens, **payload, **kwargs)
    for chunk in response:
        yield stream_openai_native(chunk)

async def stream_async(query, image=None, history=None, prefill=None, prediction=None, system=C.system, api_key=None, model=P.openai.chat_model, max_tokens=None, base_url=None, **kwargs):
    client = make_client(async_client=True, base_url=base_url, api_key=api_key)
    payload = make_payload(query, image=image, prediction=prediction, system=system, history=history)
    response = await client.chat.completions.create(model=model, stream=True, max_completion_tokens=max_tokens, **payload, **kwargs)
    async for chunk in response:
        yield stream_openai_native(chunk)

def embed(query, model=P.openai.embed_model, api_key=None, base_url=None, **kwargs):
    client = make_client(base_url=base_url, api_key=api_key)
    response = client.embeddings.create(input=query, model=model, **kwargs)
    return embed_response_openai_native(response)

def transcribe(audio, model=P.openai.transcribe_model, api_key=None, base_url=None, **kwargs):
    client = make_client(base_url=base_url, api_key=api_key)
    response = client.audio.transcriptions.create(audio, model=model, **kwargs)
    return transcribe_response_openai(response)
