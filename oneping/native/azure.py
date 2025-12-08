# azure interfaces

import os
import openai

from ..providers import (
    CONFIG as C, PROVIDERS as P,
    content_openai, convert_history, payload_openai,
    response_openai_native, stream_openai_native,
    embed_response_openai, transcribe_response_openai,
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

def make_client(azure_endpoint, async_client=False, azure_deployment=None, api_key=None):
    api_key = api_key if api_key is not None else os.environ.get(P.azure.api_key_env)
    client_class = openai.AsyncAzureOpenAI if async_client else openai.AzureOpenAI
    return client_class(azure_endpoint=azure_endpoint, azure_deployment=azure_deployment, api_version=P.azure.api_version, api_key=api_key)

def reply(
    query, image=None, history=None, prefill=None, prediction=None, system=C.system, model=P.azure.chat_model, azure_endpoint=None, azure_deployment=None, api_key=None, **kwargs
):
    client = make_client(azure_endpoint, api_key=api_key, azure_deployment=azure_deployment)
    payload = make_payload(query, image=image, prediction=prediction, system=system, history=history)
    response = client.chat.completions.create(model=model, **payload, **kwargs)
    return response_openai_native(response)

async def reply_async(
    query, image=None, history=None, prefill=None, prediction=None, system=C.system, model=P.azure.chat_model,
    azure_endpoint=None, azure_deployment=None, api_key=None, **kwargs
):
    client = make_client(azure_endpoint, api_key=api_key, azure_deployment=azure_deployment, async_client=True)
    payload = make_payload(query, image=image, prediction=prediction, system=system, history=history)
    response = await client.chat.completions.create(model=model, **payload, **kwargs)
    return response_openai_native(response)

def stream(
    query, image=None, history=None, prefill=None, prediction=None, system=C.system, model=P.azure.chat_model,
    azure_endpoint=None, azure_deployment=None, api_key=None, **kwargs
):
    client = make_client(azure_endpoint, api_key=api_key, azure_deployment=azure_deployment)
    payload = make_payload(query, image=image, prediction=prediction, system=system, history=history)
    response = client.chat.completions.create(model=model, stream=True, **payload, **kwargs)
    for chunk in response:
        yield stream_openai_native(chunk)

async def stream_async(
    query, image=None, history=None, prefill=None, prediction=None, system=C.system, model=P.azure.chat_model,
    azure_endpoint=None, azure_deployment=None, api_key=None, **kwargs
):
    client = make_client(azure_endpoint, api_key=api_key, azure_deployment=azure_deployment, async_client=True)
    payload = make_payload(query, image=image, prediction=prediction, system=system, history=history)
    response = await client.chat.completions.create(model=model, stream=True, **payload, **kwargs)
    for chunk in response:
        yield stream_openai_native(chunk)

def embed(
    query, model=P.azure.embed_model, azure_endpoint=None, azure_deployment=None, api_key=None, **kwargs
):
    client = make_client(azure_endpoint, api_key=api_key, azure_deployment=azure_deployment)
    response = client.embeddings.create(model=model, **kwargs)
    return embed_response_openai(response)

def transcribe(
    audio, model=P.azure.transcribe_model, azure_endpoint=None, azure_deployment=None, api_key=None, **kwargs
):
    client = make_client(azure_endpoint, api_key=api_key, azure_deployment=azure_deployment)
    response = client.audio.transcriptions.create(model=model, file=audio, **kwargs)
    return transcribe_response_openai(response)
