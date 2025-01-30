# azure interfaces

import os
import openai

from ..providers import (
    DEFAULT_SYSTEM, OPENAI_MODEL, OPENAI_EMBED, OPENAI_WHISPER, AZURE_API_VERSION, AZURE_KEYENV,
    payload_openai, response_openai_native, stream_openai_native, transcribe_openai
)

def make_client(azure_endpoint, azure_deployment=None, api_version=AZURE_API_VERSION, api_key=None, async_client=False):
    api_key = api_key if api_key is not None else os.environ.get(AZURE_KEYENV)
    client_class = openai.AsyncAzureOpenAI if async_client else openai.AzureOpenAI
    return client_class(azure_endpoint=azure_endpoint, azure_deployment=azure_deployment, api_version=api_version, api_key=api_key)

def reply(
    query, history=None, system=DEFAULT_SYSTEM, model=OPENAI_MODEL,
    azure_endpoint=None, azure_deployment=None, api_version=AZURE_API_VERSION, api_key=None, **kwargs
):
    client = make_client(azure_endpoint, azure_deployment=azure_deployment, api_version=api_version, api_key=api_key)
    payload = payload_openai(query, system=system, history=history)
    response = client.chat.completions.create(model=model, **payload, **kwargs)
    return response_openai_native(response)

async def reply_async(
    query, history=None, system=DEFAULT_SYSTEM, model=OPENAI_MODEL,
    azure_endpoint=None, azure_deployment=None, api_version=AZURE_API_VERSION, api_key=None, **kwargs
):
    client = make_client(azure_endpoint, azure_deployment=azure_deployment, api_version=api_version, api_key=api_key, async_client=True)
    payload = payload_openai(query, system=system, history=history)
    response = await client.chat.completions.create(model=model, **payload, **kwargs)
    return response_openai_native(response)

def stream(
    query, history=None, system=DEFAULT_SYSTEM, model=OPENAI_MODEL,
    azure_endpoint=None, azure_deployment=None, api_version=AZURE_API_VERSION, api_key=None, **kwargs
):
    client = make_client(azure_endpoint, azure_deployment=azure_deployment, api_version=api_version, api_key=api_key)
    payload = payload_openai(query, system=system, history=history)
    response = client.chat.completions.create(model=model, stream=True, **payload, **kwargs)
    for chunk in response:
        yield stream_openai_native(chunk)

async def stream_async(
    query, history=None, system=DEFAULT_SYSTEM, model=OPENAI_MODEL,
    azure_endpoint=None, azure_deployment=None, api_version=AZURE_API_VERSION, api_key=None, **kwargs
):
    client = make_client(azure_endpoint, azure_deployment=azure_deployment, api_version=api_version, api_key=api_key, async_client=True)
    payload = payload_openai(query, system=system, history=history)
    response = await client.chat.completions.create(model=model, stream=True, **payload, **kwargs)
    for chunk in response:
        yield stream_openai_native(chunk)

def embed(
    query, model=OPENAI_EMBED, azure_endpoint=None, azure_deployment=None, api_version=AZURE_API_VERSION, api_key=None, **kwargs
):
    client = make_client(azure_endpoint, azure_deployment=azure_deployment, api_version=api_version, api_key=api_key)
    response = client.embeddings.create(model=model, **kwargs)
    return embed_openai(response)

def transcribe(
    audio, model=OPENAI_WHISPER, azure_endpoint=None, azure_deployment=None, api_version=AZURE_API_VERSION, api_key=None, **kwargs
):
    client = make_client(azure_endpoint, azure_deployment=azure_deployment, api_version=api_version, api_key=api_key)
    response = client.audio.transcriptions.create(model=model, file=audio, **kwargs)
    return transcribe_openai(response)
