# llm requests

import os
import json
import requests

from .default import (
    SYSTEM, ANTHROPIC_MODEL, OPENAI_MODEL,
    payload_openai, payload_anthropic,
    response_openai, response_anthropic,
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
    },
    'anthropic': {
        'url': 'https://api.anthropic.com/v1/messages',
        'payload': payload_anthropic,
        'authorize': authorize_anthropic,
        'response': response_anthropic,
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
        'api_key_env': 'OPENAI_API_KEY', 
        'model': OPENAI_MODEL,
    },
    'fireworks': {
        'url': 'https://api.fireworks.ai/inference/v1/chat/completions',
        'payload': payload_openai,
        'authorize': authorize_openai,
        'response': response_openai,
        'api_key_env': 'FIREWORKS_API_KEY',
        'model': 'accounts/fireworks/models/llama-v3-70b-instruct',
    },
}

def get_llm_response(
    prompt, provider='local', system=SYSTEM, url=None, port=8000, api_key=None, model=None, max_tokens=1024, **kwargs
):
    # external provider
    prov = LLM_PROVIDERS[provider]

    # get url to request
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
    payload_message = prov['payload'](system, prompt)

    # base payload
    headers = {'Content-Type': 'application/json', **headers_auth, **headers_extra}
    payload = {**payload_model, **payload_message, 'max_tokens': max_tokens, **kwargs}

    # request response and return
    data = json.dumps(payload)
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    reply = response.json()

    # get text reply from data
    if (text := prov['response'](reply)) is None:
        raise Exception('No valid text response generated')

    # otherwise result text
    return text.strip()
