# google interfaces

import os

from google import genai
from google.genai.types import Part, Content, GenerateContentConfig

from ..providers import DEFAULT_SYSTEM, GOOGLE_MODEL, GOOGLE_EMBED, GOOGLE_KEYENV
from ..utils import parse_image_uri

##
## helper functions
##

def make_content(text, image=None):
    parts = [Part(text=text)]
    if image is not None:
        mime_type, data = parse_image_uri(image)
        part = Part.from_bytes(data=data, mime_type=mime_type)
        parts.append(part)
    return parts

def convert_role(role):
    if role == 'assistant':
        return 'model'
    else:
        return role

def convert_content(content):
    if type(content) is str:
        return make_content(content)
    else:
        return make_content(content['text'], image=content.get('image'))

def convert_history(history):
    if history is None:
        return None
    return [
        Content(
            role=convert_role(message['role']),
            parts=convert_content(message['content'])
        )
        for message in history
    ]

def make_config(system=DEFAULT_SYSTEM, max_tokens=None):
    return GenerateContentConfig(systemInstruction=system, maxOutputTokens=max_tokens)

def make_chat(client, model=GOOGLE_MODEL, history=None, **kwargs):
    config = make_config(**kwargs)
    history = convert_history(history)
    return client.chats.create(model=model, config=config, history=history)

##
## common interface
##

def make_client(api_key=None, async_client=False):
    api_key = api_key if api_key is not None else os.environ.get(GOOGLE_KEYENV)
    client = genai.client.Client(api_key=api_key)
    return genai.client.AsyncClient(client) if async_client else client

def reply(query, image=None, history=None, prefill=None, prediction=None, system=DEFAULT_SYSTEM, api_key=None, model=GOOGLE_MODEL, **kwargs):
    client = make_client(api_key=api_key)
    chat = make_chat(client, model=model, system=system, history=history, **kwargs)
    content = make_content(query, image=image)
    response = chat.send_message(content)
    return response.text

async def reply_async(query, image=None, history=None, prefill=None, prediction=None, system=DEFAULT_SYSTEM, api_key=None, model=GOOGLE_MODEL, **kwargs):
    client = make_client(api_key=api_key, async_client=True)
    chat = make_chat(client, model=model, system=system, history=history, **kwargs)
    content = make_content(query, image=image)
    response = await chat.send_message(content)
    return response.text

def stream(query, image=None, history=None, prefill=None, prediction=None, system=DEFAULT_SYSTEM, api_key=None, model=GOOGLE_MODEL, **kwargs):
    client = make_client(api_key=api_key)
    chat = make_chat(client, model=model, system=system, history=history, **kwargs)
    content = make_content(query, image=image)
    stream = chat.send_message_stream(content)
    for chunk in stream:
        yield chunk.text

async def stream_async(query, image=None, history=None, prefill=None, prediction=None, system=DEFAULT_SYSTEM, api_key=None, model=GOOGLE_MODEL, **kwargs):
    client = make_client(api_key=api_key, async_client=True)
    chat = make_chat(client, model=model, system=system, history=history, **kwargs)
    content = make_content(query, image=image)
    stream = await chat.send_message_stream(content)
    async for chunk in stream:
        yield chunk.text

def embed(text, api_key=None, model=GOOGLE_EMBED):
    client = make_client(api_key=api_key)
    response = client.models.embed_content(model=model, content=text)
    return response.embeddings[0].values
