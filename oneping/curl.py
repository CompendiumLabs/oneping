# llm requests

import os
import json
import requests
import aiohttp

from .providers import get_provider
from .utils import syncify

##
## payloads
##

def strip_system(messages):
    if len(messages) == 0:
        return messages
    if messages[0]['role'] == 'system':
        return messages[1:]
    return messages

def compose_history(history, content):
    if len(history) == 0:
        return [{'role': 'user', 'content': content}]
    last = history[-1]

    # are we in prefill?
    last_role, last_content = last['role'], last['content']
    if last_role == 'assistant':
        return history[:-1] + [
            {'role': 'assistant', 'content': last_content + content},
        ]

    # usual case
    return history + [{'role': 'assistant', 'content': content}]

def prepare_request(
    prompt, provider='local', system=None, prefill=None, history=None, url=None,
    port=8000, api_key=None, model=None, max_tokens=1024, **kwargs
):
    # external provider
    prov = get_provider(provider)

    # get max_tokens name (might be max_completion_tokens for openai)
    max_tokens_name = prov.get('max_tokens_name', 'max_tokens')

    # get full url
    if url is None:
        url = prov['url'].format(port=port)

    # get authorization headers
    if (auth_func := prov.get('authorize')) is not None:
        if api_key is None and (api_key := os.environ.get(key_env := prov['api_key_env'])) is None:
            raise Exception('Cannot find API key in {key_env}')
        headers_auth = auth_func(api_key)
    else:
        headers_auth = {}

    # get extra headers
    headers_extra = prov.get('headers', {})

    # get default model
    if model is None:
        model = prov.get('model')
    payload_model = {'model': model} if model is not None else {}

    # get message payload
    payload_message = prov['payload'](prompt=prompt, system=system, prefill=prefill, history=history)

    # base payload
    headers = {'Content-Type': 'application/json', **headers_auth, **headers_extra}
    payload = {**payload_model, **payload_message, max_tokens_name: max_tokens, **kwargs}

    # return url, headers, payload
    return url, headers, payload

##
## requests
##

def reply(prompt, provider='local', history=None, **kwargs):
    # get provider
    prov = get_provider(provider)

    # prepare request
    url, headers, payload = prepare_request(prompt, provider=provider, history=history, **kwargs)

    # request response and return
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    response.raise_for_status()
    data = response.json()

    # extract text
    extractor = prov['response']
    text = extractor(data)

    # update history
    if history is not None:
        history_sent = strip_system(payload['messages'])
        return compose_history(history_sent, text), text

    # just return text
    return text

##
## stream requests
##

async def iter_lines_buffered(inputs):
    buffer = b''
    async for chunk in inputs:
        buffer += chunk
        lines = buffer.split(b'\n')
        buffer = lines.pop()
        for line in lines:
            if len(line) > 0:
                yield line
    if len(buffer) > 0:
        yield buffer

async def parse_stream_async(inputs):
    async for chunk in inputs:
        if len(chunk) == 0:
            continue
        elif chunk.startswith(b'data: '):
            text = chunk[6:]
            if text == b'[DONE]':
                break
            yield text

async def stream_async(prompt, provider='local', history=None, prefill=None, **kwargs):
    # get provider
    prov = get_provider(provider)

    # prepare request
    url, headers, payload = prepare_request(prompt, provider=provider, history=history, **kwargs)

    # augment headers/payload
    headers['Accept'] = 'text/event-stream'
    payload['stream'] = True

    # request stream object
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=json.dumps(payload)) as response:
            # check for errors
            response.raise_for_status()

            # extract stream contents
            chunks = response.content.iter_chunked(1024)
            lines = iter_lines_buffered(chunks)
            parsed = parse_stream_async(lines)

            # yield prefill for consistency
            if prefill is not None:
                yield prefill

            # extract stream contents
            extractor = prov['stream']
            async for text in parsed:
                data = json.loads(text)
                yield extractor(data)

def stream(prompt, **kwargs):
    response = stream_async(prompt, **kwargs)
    return syncify(response)
