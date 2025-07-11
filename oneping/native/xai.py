# openai interfaces

import os
from xai_sdk import Client, AsyncClient
from xai_sdk.chat import system as _system, user as _user, assistant as _assistant, image as _image, text as _text

from ..providers import DEFAULT_SYSTEM, XAI_MODEL, XAI_KEYENV

##
## helper functions
##

# handle string case
def convert_content(content):
    if type(content) is str:
        return [content]
    elif type(content) is dict:
        parts = []
        if 'text' in content:
            text = content['text']
            parts.append(_text(text))
        if 'image' in content:
            image = content['image']
            parts.append(_image(image))
        return parts
    else:
        raise ValueError(f'Unknown content type: {type(content)}')

def convert_message(message):
    role = message['role']
    content0 = message['content']
    content = convert_content(content0)
    if role == 'user':
        return _user(*content)
    elif role == 'assistant':
        return _assistant(*content)
    else:
        raise ValueError(f'Unknown role: {role}')

def convert_history(history):
    return [convert_message(message) for message in history]

def make_chat(client, model, query=None, image=None, system=None, history=None, max_tokens=None):
    # make base message history
    messages = []
    if system is not None:
        messages.append(_system(system))
    if history is not None:
        messages.extend(convert_history(history))

    # make new user query
    parts = []
    if query is not None:
        parts.append(_text(query))
    if image is not None:
        parts.append(_image(image))
    messages.append(_user(*parts))

    # make chat object
    return client.chat.create(model=model, messages=messages, max_tokens=max_tokens)

def make_client(api_key=None, async_client=False):
    api_key = api_key if api_key is not None else os.environ.get(XAI_KEYENV)
    client_class = AsyncClient if async_client else Client
    return client_class(api_key=api_key)

##
## common interface
##

def reply(query, image=None, history=None, prefill=None, prediction=None, system=DEFAULT_SYSTEM, api_key=None, model=XAI_MODEL, max_tokens=None, **kwargs):
    client = make_client(api_key=api_key)
    chat = make_chat(client, model, query, image=image, system=system, history=history, max_tokens=max_tokens)
    response = chat.sample()
    return response.content

async def reply_async(query, image=None, history=None, prefill=None, prediction=None, system=DEFAULT_SYSTEM, api_key=None, model=XAI_MODEL, max_tokens=None, **kwargs):
    client = make_client(api_key=api_key, async_client=True)
    chat = make_chat(client, model, query, image=image, system=system, history=history, max_tokens=max_tokens)
    response = await chat.sample()
    return response.content

def stream(query, image=None, history=None, prefill=None, prediction=None, system=DEFAULT_SYSTEM, api_key=None, model=XAI_MODEL, max_tokens=None, **kwargs):
    client = make_client(api_key=api_key)
    chat = make_chat(client, model, query, image=image, system=system, history=history, max_tokens=max_tokens)
    for response, chunk in chat.stream():
        yield chunk.content

async def stream_async(query, image=None, history=None, prefill=None, prediction=None, system=DEFAULT_SYSTEM, api_key=None, model=XAI_MODEL, max_tokens=None, **kwargs):
    client = make_client(api_key=api_key, async_client=True)
    chat = make_chat(client, model, query, image=image, system=system, history=history, max_tokens=max_tokens)
    async for response, chunk in chat.stream():
        yield chunk.content
