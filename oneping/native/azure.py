# azure interfaces

import os
import openai

from ..providers import (
    DEFAULT_SYSTEM, OPENAI_MODEL, OPENAI_EMBED, OPENAI_TRANSCRIBE, AZURE_API_VERSION, AZURE_KEYENV,
    content_openai, convert_history, payload_openai,
    response_openai_native, stream_openai_native,
    embed_response_openai, transcribe_response_openai
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

def make_client(azure_endpoint, azure_deployment=None, api_version=AZURE_API_VERSION, api_key=None, async_client=False):
    api_key = api_key if api_key is not None else os.environ.get(AZURE_KEYENV)
    client_class = openai.AsyncAzureOpenAI if async_client else openai.AzureOpenAI
    return client_class(azure_endpoint=azure_endpoint, azure_deployment=azure_deployment, api_version=api_version, api_key=api_key)

def reply(
    query, image=None, history=None, prefill=None, prediction=None, system=DEFAULT_SYSTEM, model=OPENAI_MODEL,
    azure_endpoint=None, azure_deployment=None, api_version=AZURE_API_VERSION, api_key=None, **kwargs
):
    client = make_client(azure_endpoint, azure_deployment=azure_deployment, api_version=api_version, api_key=api_key)
    payload = make_payload(query, image=image, prediction=prediction, system=system, history=history)
    response = client.chat.completions.create(model=model, **payload, **kwargs)
    return response_openai_native(response)

async def reply_async(
    query, image=None, history=None, prefill=None, prediction=None, system=DEFAULT_SYSTEM, model=OPENAI_MODEL,
    azure_endpoint=None, azure_deployment=None, api_version=AZURE_API_VERSION, api_key=None, **kwargs
):
    client = make_client(azure_endpoint, azure_deployment=azure_deployment, api_version=api_version, api_key=api_key, async_client=True)
    payload = make_payload(query, image=image, prediction=prediction, system=system, history=history)
    response = await client.chat.completions.create(model=model, **payload, **kwargs)
    return response_openai_native(response)

def stream(
    query, image=None, history=None, prefill=None, prediction=None, system=DEFAULT_SYSTEM, model=OPENAI_MODEL,
    azure_endpoint=None, azure_deployment=None, api_version=AZURE_API_VERSION, api_key=None, **kwargs
):
    client = make_client(azure_endpoint, azure_deployment=azure_deployment, api_version=api_version, api_key=api_key)
    payload = make_payload(query, image=image, prediction=prediction, system=system, history=history)
    response = client.chat.completions.create(model=model, stream=True, **payload, **kwargs)
    for chunk in response:
        yield stream_openai_native(chunk)

async def stream_async(
    query, image=None, history=None, prefill=None, prediction=None, system=DEFAULT_SYSTEM, model=OPENAI_MODEL,
    azure_endpoint=None, azure_deployment=None, api_version=AZURE_API_VERSION, api_key=None, **kwargs
):
    client = make_client(azure_endpoint, azure_deployment=azure_deployment, api_version=api_version, api_key=api_key, async_client=True)
    payload = make_payload(query, image=image, prediction=prediction, system=system, history=history)
    response = await client.chat.completions.create(model=model, stream=True, **payload, **kwargs)
    for chunk in response:
        yield stream_openai_native(chunk)

def embed(
    query, model=OPENAI_EMBED, azure_endpoint=None, azure_deployment=None, api_version=AZURE_API_VERSION, api_key=None, **kwargs
):
    client = make_client(azure_endpoint, azure_deployment=azure_deployment, api_version=api_version, api_key=api_key)
    response = client.embeddings.create(model=model, **kwargs)
    return embed_response_openai(response)

def transcribe(
    audio, model=OPENAI_TRANSCRIBE, azure_endpoint=None, azure_deployment=None, api_version=AZURE_API_VERSION, api_key=None, **kwargs
):
    client = make_client(azure_endpoint, azure_deployment=azure_deployment, api_version=api_version, api_key=api_key)
    response = client.audio.transcriptions.create(model=model, file=audio, **kwargs)
    return transcribe_response_openai(response)
