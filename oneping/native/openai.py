# openai interfaces

import os
import openai

from ..providers import (
    DEFAULT_SYSTEM, OPENAI_MODEL, OPENAI_EMBED, OPENAI_WHISPER, OPENAI_KEYENV,
    content_openai, convert_history, payload_openai,
    response_openai_native, stream_openai_native,
    embed_openai, transcribe_openai
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

def make_client(api_key=None, async_client=False):
    api_key = api_key if api_key is not None else os.environ.get(OPENAI_KEYENV)
    client_class = openai.AsyncOpenAI if async_client else openai.OpenAI
    return client_class(api_key=api_key)

def reply(query, image=None, history=None, system=DEFAULT_SYSTEM, api_key=None, model=OPENAI_MODEL, **kwargs):
    client = make_client(api_key=api_key)
    payload = make_payload(query, image=image, system=system, history=history)
    response = client.chat.completions.create(model=model, **payload, **kwargs)
    return response_openai_native(response)

async def reply_async(query, image=None, history=None, system=DEFAULT_SYSTEM, api_key=None, model=OPENAI_MODEL, **kwargs):
    client = make_client(api_key=api_key, async_client=True)
    payload = make_payload(query, image=image, system=system, history=history)
    response = await client.chat.completions.create(model=model, **payload, **kwargs)
    return response_openai_native(response)

def stream(query, image=None, history=None, system=DEFAULT_SYSTEM, api_key=None, model=OPENAI_MODEL, **kwargs):
    client = make_client(api_key=api_key)
    payload = make_payload(query, image=image, system=system, history=history)
    response = client.chat.completions.create(model=model, stream=True, **payload, **kwargs)
    for chunk in response:
        yield stream_openai_native(chunk)

async def stream_async(query, image=None, history=None, system=DEFAULT_SYSTEM, api_key=None, model=OPENAI_MODEL, **kwargs):
    client = make_client(api_key=api_key, async_client=True)
    payload = make_payload(query, image=image, system=system, history=history)
    response = await client.chat.completions.create(model=model, stream=True, **payload, **kwargs)
    async for chunk in response:
        yield stream_openai_native(chunk)

def embed(query, model=OPENAI_EMBED, api_key=None, **kwargs):
    client = make_client(api_key=api_key)
    response = client.embeddings.create(model=model, **kwargs)
    return embed_openai(response)

def transcribe(audio, model=OPENAI_WHISPER, api_key=None, **kwargs):
    client = make_client(api_key=api_key)
    response = client.audio.transcriptions.create(model=model, **kwargs)
    return transcribe_openai(response)
