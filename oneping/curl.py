# llm requests

import os
import json
import requests
import aiohttp

from .providers import get_provider, convert_history, DEFAULT_MAX_TOKENS

##
## printing
##

def print_dryrun(url, headers, payload):
    from rich import print_json
    print(f'URL: {url}')
    print('HEADERS:')
    print_json(data=headers)
    print('PAYLOAD:')
    print_json(data=payload)

##
## payloads
##

def prepare_url(prov, path_key, base_url=None, path=None):
    base_url = prov.get('base_url') if base_url is None else base_url
    path = prov.get(path_key) if path is None else path
    return f'{base_url}/{path}'

def prepare_model(prov, model_key, model=None):
    if model is None:
        model = prov.get(model_key)
    return {'model': model} if model is not None else {}

def prepare_auth(prov, api_key=None):
    if (auth_func := prov.get('authorize')) is not None:
        if (api_key := os.environ.get(prov['api_key_env'])) is None:
            raise Exception('Cannot find API key in {api_key_env}')
        headers_auth = auth_func(api_key)
    else:
        headers_auth = {}
    return headers_auth

def prepare_request(
    query, provider='local', system=None, image=None, prefill=None, prediction=None, history=None,
    base_url=None, path=None, api_key=None, model=None, max_tokens=DEFAULT_MAX_TOKENS, **kwargs
):
    # external provider details
    prov = get_provider(provider)
    max_tokens_name = prov.get('max_tokens_name', 'max_completion_tokens')
    url = prepare_url(prov, 'chat_path', base_url=base_url, path=path)
    payload_model = prepare_model(prov, 'chat_model', model=model)

    # convert history to provider format
    history = convert_history(history, prov['content'])

    # get extra headers
    headers_auth = prepare_auth(prov, api_key=api_key)
    headers_extra = prov.get('headers', {})

    # get message payload
    content = prov['content'](query, image=image)
    payload_message = prov['payload'](
        content, system=system, prefill=prefill, prediction=prediction, history=history
    )

    # compose request
    headers = {'Content-Type': 'application/json', **headers_auth, **headers_extra}
    payload = {**payload_model, **payload_message, max_tokens_name: max_tokens, **kwargs}

    # return url, headers, payload
    return url, headers, payload

##
## requests
##

def reply(query, provider='local', history=None, prefill=None, dryrun=False, **kwargs):
    # get provider
    prov = get_provider(provider)
    extractor = prov['response']

    # prepare request
    url, headers, payload = prepare_request(
        query, provider=provider, history=history, prefill=prefill, **kwargs
    )

    # just print the request
    if dryrun:
        print_dryrun(url, headers, payload)
        return

    # request response and return
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    response.raise_for_status()

    # extract text
    data = response.json()
    text = extractor(data)

    # add in prefill
    if prefill is not None:
        text = prefill + text

    # return text
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

    # return text
    return text

##
## stream requests
##

def parse_sse(line):
    if line.startswith(b'data: '):
        text = line[6:]
        if text != b'[DONE]' and len(text) > 0:
            return text

async def iter_lines(inputs):
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
            if (data := parse_sse(line)) is not None:
                parsed = json.loads(data)
                text = extractor(parsed)
                if text is not None:
                    yield text

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
            chunks = response.content.iter_any()

            # yield prefill
            if prefill is not None:
                yield prefill

            # extract stream contents
            async for line in iter_lines(chunks):
                if (data := parse_sse(line)) is not None:
                    parsed = json.loads(data)
                    text = extractor(parsed)
                    if text is not None:
                        yield text

##
## embeddings
##

def embed(text, provider='local', base_url=None, path=None, api_key=None, model=None, **kwargs):
    # get provider details
    prov = get_provider(provider)
    url = prepare_url(prov, 'embed_path', base_url=base_url, path=path)
    payload_model = prepare_model(prov, 'embed_model', model=model)

    # get extra headers
    headers_auth = prepare_auth(prov, api_key=api_key)
    headers_extra = prov.get('headers', {})

    # compose request
    headers = {'Content-Type': 'application/json', **headers_auth, **headers_extra}
    payload = {'input': text, **payload_model, **kwargs}

    # make the request
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    response.raise_for_status()

    # extract text
    data = response.json()
    vecs = prov['embed'](data)

    # return text
    return vecs
