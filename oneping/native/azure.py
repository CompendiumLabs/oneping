# openai interfaces

from openai import AzureOpenAI

from ..providers import (
    DEFAULT_SYSTEM, OPENAI_MODEL, OPENAI_EMBED, payload_openai,
    response_openai_native, stream_openai_native, transcribe_openai
)

def reply(
    query, history=None, system=DEFAULT_SYSTEM, model=OPENAI_MODEL,
    api_version=AZURE_API_VERSION, api_key=None, endpoint=None, **kwargs
):
    # construct client and payload
    client = AzureOpenAI(api_key=api_key, api_version=api_version, azure_endpoint=endpoint)
    payload = payload_openai(query, system=system, history=history)

    # get response and convert to text
    response = client.chat.completions.create(model=model, **payload, **kwargs)
    return response_openai_native(response)

async def reply_async(
    query, history=None, system=DEFAULT_SYSTEM, model=OPENAI_MODEL,
    api_version=AZURE_API_VERSION, api_key=None, endpoint=None, **kwargs
):
    # construct client and payload
    client = AsyncAzureOpenAI(api_key=api_key, api_version=api_version, azure_endpoint=endpoint)
    payload = payload_openai(query, system=system, history=history)

    # get response and convert to text
    response = await client.chat.completions.create(model=model, **payload, **kwargs)
    return response_openai_native(response)

def stream(
    query, history=None, system=DEFAULT_SYSTEM, model=OPENAI_MODEL,
    api_version=AZURE_API_VERSION, api_key=None, endpoint=None, **kwargs
):
    # construct client and payload
    client = AzureOpenAI(api_key=api_key, api_version=api_version, azure_endpoint=endpoint)
    payload = payload_openai(query, system=system, history=history)

    # stream response
    response = client.chat.completions.create(model=model, stream=True, **payload, **kwargs)
    for chunk in response:
        yield stream_openai_native(chunk)

async def stream_async(
    query, history=None, system=DEFAULT_SYSTEM, model=OPENAI_MODEL,
    api_version=AZURE_API_VERSION, api_key=None, endpoint=None, **kwargs
):
    # construct client and payload
    client = AsyncAzureOpenAI(api_key=api_key, api_version=api_version, azure_endpoint=endpoint)
    payload = payload_openai(query, system=system, history=history)

    # stream response
    response = await client.chat.completions.create(model=model, stream=True, **payload, **kwargs)
    async for chunk in response:
        yield stream_openai_native(chunk)

# audio should be a file-like object
def transcribe(
    audio, model='whisper-1', api_version=AZURE_API_VERSION, api_key=None, endpoint=None, **kwargs
):
    client = AzureOpenAI(api_key=api_key, api_version=api_version, azure_endpoint=endpoint)
    response = client.audio.transcriptions.create(model=model, file=audio)
    return transcribe_openai(response)
