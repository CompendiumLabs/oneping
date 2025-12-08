# groq interfaces

import os
import groq

from ..providers import (
    CONFIG as C, PROVIDERS as P,
    content_openai, convert_history, payload_openai,
    response_openai_native, stream_openai_native
)

##
## helper functions
##

def make_payload(query, image=None, system=None, history=None):
    content = content_openai(query, image=image)
    history = convert_history(history, content_openai)
    return payload_openai(content, system=system, history=history)

##
## common interface
##

def make_client(async_client=False, api_key=None):
    api_key = api_key if api_key is not None else os.environ.get(P.groq.api_key_env)
    client_class = groq.AsyncGroq if async_client else groq.Groq
    return client_class(api_key=api_key)

def reply(query, image=None, history=None, prefill=None, prediction=None, system=C.system, api_key=None, model=P.groq.chat_model, **kwargs):
    client = make_client(api_key=api_key)
    payload = make_payload(query, image=image, system=system, history=history)
    response = client.chat.completions.create(model=model, **payload, **kwargs)
    return response_openai_native(response)

async def reply_async(query, image=None, history=None, prefill=None, prediction=None, system=C.system, api_key=None, model=P.groq.chat_model, **kwargs):
    client = make_client(api_key=api_key, async_client=True)
    payload = make_payload(query, image=image, system=system, history=history)
    response = await client.chat.completions.create(model=model, **payload, **kwargs)
    return response_openai_native(response)

def stream(query, image=None, history=None, prefill=None, prediction=None, system=C.system, api_key=None, model=P.groq.chat_model, **kwargs):
    client = make_client(api_key=api_key)
    payload = make_payload(query, image=image, system=system, history=history)
    response = client.chat.completions.create(model=model, stream=True, **payload, **kwargs)
    for chunk in response:
        yield stream_openai_native(chunk)

async def stream_async(query, image=None, history=None, prefill=None, prediction=None, system=C.system, api_key=None, model=P.groq.chat_model, **kwargs):
    client = make_client(api_key=api_key, async_client=True)
    payload = make_payload(query, image=image, system=system, history=history)
    response = await client.chat.completions.create(model=model, stream=True, **payload, **kwargs)
    async for chunk in response:
        yield stream_openai_native(chunk)
