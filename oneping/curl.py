# llm requests

import os
import json
import requests
import aiohttp

from .providers import get_provider, get_embed_provider, DEFAULT_MAX_TOKENS

##
## history
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

##
## payloads
##

def prepare_url(prov, url=None, port=None):
    if port is None:
        port = 8000
    if url is None:
        url = prov['url'].format(port=port)
    return url

def prepare_auth(prov, api_key=None):
    if (auth_func := prov.get('authorize')) is not None:
        if api_key is None and (api_key := os.environ.get(key_env := prov['api_key_env'])) is None:
            raise Exception('Cannot find API key in {key_env}')
        headers_auth = auth_func(api_key)
    else:
        headers_auth = {}
    return headers_auth

def prepare_model(prov, model=None):
    if model is None:
        model = prov.get('model')
    return {'model': model} if model is not None else {}

def prepare_request(
    query, provider='local', system=None, prefill=None, history=None, url=None,
    port=None, api_key=None, model=None, max_tokens=DEFAULT_MAX_TOKENS, **kwargs
):
    # external provider
    prov = get_provider(provider)

    # get max_tokens name (might be max_completion_tokens for openai)
    max_tokens_name = prov.get('max_tokens_name', 'max_tokens')

    # get full url
    url = prepare_url(prov, url=url, port=port)

    # get authorization headers
    headers_auth = prepare_auth(prov, api_key=api_key)

    # get extra headers
    headers_extra = prov.get('headers', {})

    # get default model
    payload_model = prepare_model(prov, model=model)

    # get message payload
    payload_message = prov['payload'](query=query, system=system, prefill=prefill, history=history)

    # base payload
    headers = {'Content-Type': 'application/json', **headers_auth, **headers_extra}
    payload = {**payload_model, **payload_message, max_tokens_name: max_tokens, **kwargs}

    # return url, headers, payload
    return url, headers, payload

##
## requests
##

def reply(query, provider='local', history=None, prefill=None, **kwargs):
    # get provider
    prov = get_provider(provider)
    extractor = prov['response']

    # prepare request
    url, headers, payload = prepare_request(
        query, provider=provider, history=history, prefill=prefill, **kwargs
    )

    # request response and return
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    response.raise_for_status()

    # extract text
    data = response.json()
    text = extractor(data)

    # add in prefill
    if prefill is not None:
        text = prefill + text

    # update history
    if history is not None:
        history_sent = strip_system(payload['messages'])
        history_next = compose_history(history_sent, text)
        return history_next, text

    # just return text
    return text

async def reply_async(query, provider='local', history=None, prefill=None, **kwargs):
    # get provider
    prov = get_provider(provider)
    extractor = prov['response']

    # prepare request
    url, headers, payload = prepare_request(
        query, provider=provider, history=history, prefill=prefill, **kwargs
    )

    # request response and return
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=json.dumps(payload)) as response:
            response.raise_for_status()

            # extract text
            data = await response.json()
            text = extractor(data)

    # add in prefill
    if prefill is not None:
        text = prefill + text

    # update history
    if history is not None:
        history_sent = strip_system(payload['messages'])
        history_next = compose_history(history_sent, text)
        return history_next, text

    # just return text
    return text

##
## stream requests
##

def parse_stream_data(chunk):
    if chunk.startswith(b'data: '):
        text = chunk[6:]
        if text != b'[DONE]' and len(text) > 0:
            return text

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

def stream(query, provider='local', history=None, prefill=None, **kwargs):
    # get provider
    prov = get_provider(provider)
    extractor = prov['stream']

    # prepare request
    url, headers, payload = prepare_request(
        query, provider=provider, history=history, prefill=prefill, **kwargs
    )

    # augment headers/payload
    headers['Accept'] = 'text/event-stream'
    payload['stream'] = True

    # make the request
    with requests.post(url, headers=headers, data=json.dumps(payload), stream=True) as response:
        # check for errors
        response.raise_for_status()

        # yield prefill
        if prefill is not None:
            yield prefill

        # extract stream contents
        for line in response.iter_lines():
            if (data := parse_stream_data(line)) is not None:
                parsed = json.loads(data)
                yield extractor(parsed)

async def stream_async(query, provider='local', history=None, prefill=None, **kwargs):
    # get provider
    prov = get_provider(provider)
    extractor = prov['stream']

    # prepare request
    url, headers, payload = prepare_request(
        query, provider=provider, history=history, prefill=prefill, **kwargs
    )

    # augment headers/payload
    headers['Accept'] = 'text/event-stream'
    payload['stream'] = True

    # request stream object
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=json.dumps(payload)) as response:
            # check for errors
            response.raise_for_status()

            # yield prefill
            if prefill is not None:
                yield prefill

            # extract stream contents
            chunks = response.content.iter_any()
            lines = iter_lines_buffered(chunks)

            # extract stream contents
            async for line in lines:
                if (data := parse_stream_data(line)) is not None:
                    parsed = json.loads(data)
                    yield extractor(parsed)

##
## embeddings
##

def embed(text, provider='local', url=None, port=None, api_key=None, model=None, **kwargs):
    # get provider
    prov = get_embed_provider(provider)
    extractor = prov['embed']

    # get full url
    url = prepare_url(prov, url=url, port=port)

    # get authorization headers
    headers_auth = prepare_auth(prov, api_key=api_key)

    # get default model
    payload_model = prepare_model(prov, model=model)

    # combine payload
    headers = {'Content-Type': 'application/json', **headers_auth}
    payload = {'input': text, **payload_model}

    # make the request
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    response.raise_for_status()

    # extract text
    data = response.json()
    vecs = extractor(data)

    # return text
    return vecs
