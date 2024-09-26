# llm requests

import os
import json
import requests
import aiohttp

from .default import (
    SYSTEM, ANTHROPIC_MODEL, OPENAI_MODEL, syncify,
    payload_openai, payload_anthropic,
    response_openai, response_anthropic,
    stream_openai, stream_anthropic,
)

##
## authorization headers
##

def authorize_openai(api_key):
    return {
        'Authorization': f'Bearer {api_key}',
    }

def authorize_anthropic(api_key):
    return {
        'x-api-key': api_key,
    }

##
## known llm providers
##

# presets for known llm providers
LLM_PROVIDERS = {
    'local': {
        'url': 'http://localhost:{port}/v1/chat/completions',
        'payload': payload_openai,
        'response': response_openai,
        'stream': stream_openai,
    },
    'anthropic': {
        'url': 'https://api.anthropic.com/v1/messages',
        'payload': payload_anthropic,
        'authorize': authorize_anthropic,
        'response': response_anthropic,
        'stream': stream_anthropic,
        'api_key_env': 'ANTHROPIC_API_KEY',
        'model': ANTHROPIC_MODEL,
        'headers': {
            'anthropic-version': '2023-06-01',
            'anthropic-beta': 'prompt-caching-2024-07-31',
        },
    },
    'openai': {
        'url': 'https://api.openai.com/v1/chat/completions',
        'payload': payload_openai,
        'authorize': authorize_openai,
        'response': response_openai,
        'stream': stream_openai,
        'api_key_env': 'OPENAI_API_KEY', 
        'model': OPENAI_MODEL,
    },
    'fireworks': {
        'url': 'https://api.fireworks.ai/inference/v1/chat/completions',
        'payload': payload_openai,
        'authorize': authorize_openai,
        'response': response_openai,
        'stream': stream_openai,
        'api_key_env': 'FIREWORKS_API_KEY',
        'model': 'accounts/fireworks/models/llama-v3-70b-instruct',
    },
}

def get_provider(provider):
    if type(provider) is str:
        return LLM_PROVIDERS[provider]
    return provider

##
## requests
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
    payload = {**payload_model, **payload_message, 'max_tokens': max_tokens, **kwargs}

    # return url, headers, payload
    return url, headers, payload

##
## sync requests
##

def parse_stream(stream):
    for chunk in stream:
        if len(chunk) == 0:
            continue
        elif chunk.startswith(b'data: '):
            text = chunk[6:]
            if text == b'[DONE]':
                break
            yield text

def get_llm_response(prompt, provider='local', history=None, **kwargs):
    # get provider
    prov = get_provider(provider)

    # prepare request
    url, headers, payload = prepare_request(prompt, provider=provider, history=history, **kwargs)

    # request response and return
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    response.raise_for_status()
    reply = response.json()

    # extract text
    extractor = prov['response']
    text = extractor(reply)

    # update history
    if history is not None:
        history_sent = strip_system(payload['messages'])
        return compose_history(history_sent, text), text

    # just return text
    return text

##
## async requests
##

async def iter_lines_buffered(stream):
    buffer = b''
    async for chunk in stream:
        buffer += chunk
        lines = buffer.split(b'\n')
        buffer = lines.pop()
        for line in lines:
            if len(line) > 0:
                yield line
    if len(buffer) > 0:
        yield buffer

async def parse_stream_async(stream):
    async for chunk in stream:
        if len(chunk) == 0:
            continue
        elif chunk.startswith(b'data: '):
            text = chunk[6:]
            if text == b'[DONE]':
                break
            yield text

async def extract_stream_async(stream, extractor):
    async for js in stream:
        data = json.loads(js)
        yield extractor(data)

async def async_llm_response(prompt, provider='local', history=None, prefill=None, **kwargs):
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
            stream = iter_lines_buffered(chunks)
            parsed = parse_stream_async(stream)

            # yield prefill for consistency
            if prefill is not None:
                yield prefill

            # extract stream contents
            extractor = prov['stream']
            async for text in parsed:
                data = json.loads(text)
                yield extractor(data)

def stream_llm_response(prompt, **kwargs):
    response = async_llm_response(prompt, **kwargs)
    return syncify(response)
