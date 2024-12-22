# openai interfaces

from openai import AzureOpenAI

from ..providers import (
    DEFAULT_SYSTEM, OPENAI_MODEL, OPENAI_EMBED, payload_openai,
    response_openai_native, stream_openai_native
)

def reply(
    query, history=None, system=DEFAULT_SYSTEM, api_version=AZURE_API_VERSION, model=OPENAI_MODEL,
    api_key=None, endpoint=None, **kwargs
):
    # construct client and payload
    client = AzureOpenAI(api_key=api_key, api_version=api_version, azure_endpoint=endpoint)
    payload = payload_openai(query, system=system, history=history)

    # get response and convert to text
    response = client.chat.completions.create(model=model, **payload, **kwargs)
    return response_openai_native(response)

async def reply_async(
    query, history=None, system=DEFAULT_SYSTEM, api_version=AZURE_API_VERSION, model=OPENAI_MODEL,
    api_key=None, endpoint=None, **kwargs
):

    # handle unspecified defaults
    system = DEFAULT_SYSTEM if system is None else system
    model = OPENAI_MODEL if model is None else model

    # construct client and payload
    client = AsyncAzureOpenAI(api_key=api_key, api_version=api_version, azure_endpoint=endpoint)
    payload = payload_openai(query, system=system, history=history)

    # get response and convert to text
    response = await client.chat.completions.create(model=model, **payload, **kwargs)
    return response_openai_native(response)

def stream(
    query, history=None, system=DEFAULT_SYSTEM, api_version=AZURE_API_VERSION, model=OPENAI_MODEL,
    api_key=None, endpoint=None, **kwargs
):

    # handle unspecified defaults
    system = DEFAULT_SYSTEM if system is None else system
    model = OPENAI_MODEL if model is None else model

    # construct client and payload
    client = AzureOpenAI(api_key=api_key, api_version=api_version, azure_endpoint=endpoint)
    payload = payload_openai(query, system=system, history=history)

    # stream response
    response = client.chat.completions.create(model=model, stream=True, **payload, **kwargs)
    for chunk in response:
        yield stream_openai_native(chunk)

async def stream_async(
    query, history=None, system=DEFAULT_SYSTEM, api_version=AZURE_API_VERSION, model=OPENAI_MODEL,
    api_key=None, endpoint=None, **kwargs
):

    # handle unspecified defaults
    system = DEFAULT_SYSTEM if system is None else system
    model = OPENAI_MODEL if model is None else model

    # construct client and payload
    client = AsyncAzureOpenAI(api_key=api_key, api_version=api_version, azure_endpoint=endpoint)
    payload = payload_openai(query, system=system, history=history)

    # stream response
    response = await client.chat.completions.create(model=model, stream=True, **payload, **kwargs)
    async for chunk in response:
        yield stream_openai_native(chunk)
