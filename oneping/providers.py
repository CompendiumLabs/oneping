# default arguments

import os
import tomllib
from pathlib import Path

from .utils import split_image_uri, ensure_image_uri, Config

##
## authorization headers
##

def authorize_openai(api_key):
    return {
        'Authorization': f'Bearer {api_key}',
    }

def authorize_anthropic(api_key):
    return {
        'X-Api-Key': api_key,
    }

##
## content converters
##

def content_openai(text, image=None):
    if image is None:
        return text
    image_url = { 'url': ensure_image_uri(image) }
    return [
        { 'type': 'image_url', 'image_url': image_url },
        { 'type': 'text', 'text': text },
    ]

def content_anthropic(text, image=None):
    if image is None:
        return text
    image_url = ensure_image_uri(image)
    media_type, data = split_image_uri(image_url)
    source = {
        'type': 'base64', 'media_type': media_type, 'data': data
    }
    return [
        { 'type': 'image', 'source': source },
        { 'type': 'text', 'text': text },
    ]

def content_oneping(text, image=None):
    if image is None:
        return text
    return { 'image': image, 'text': text }

##
## history converters
##

def convert_content(content, content_func):
    data = { 'text': content } if type(content) is str else content
    return content_func(**data)

def convert_history(history, content_func):
    if history is None:
        return None
    return [
        {
            'role': item['role'],
            'content': convert_content(item['content'], content_func)
        }
        for item in history
    ]

##
## message payloads
##

def payload_openai(content, system=None, prefill=None, prediction=None, history=None):
    messages = [{'role': 'system', 'content': system}] if system is not None else []
    if history is not None:
        messages += history
    messages.append({'role': 'user', 'content': content})
    if prefill is not None:
        messages.append({'role': 'assistant', 'content': prefill})
    payload = {'messages': messages}
    if prediction is not None:
        payload['prediction'] = {'type': 'content', 'content': prediction}
    return payload

def payload_anthropic(content, system=None, prefill=None, prediction=None, history=None):
    messages = [*history] if type(history) is list else []
    messages.append({'role': 'user', 'content': content})
    if prefill is not None:
        messages.append({'role': 'assistant', 'content': prefill})
    payload = {'messages': messages}
    if system is not None:
        payload['system'] = [{
            'text': system,
            'type': 'text',
            'cache_control': {'type': 'ephemeral'},
        }]
    return payload

def payload_oneping(content, system=None, prefill=None, prediction=None, history=None):
    content = { 'text': content } if type(content) is str else content
    return {
        'query': content['text'],
        'image': content.get('image'),
        'system': system,
        'prefill': prefill,
        'prediction': prediction,
        'history': history,
    }

##
## response handlers
##

def response_oneping(reply):
    return reply

def response_openai(reply):
    choice = reply['choices'][0]
    return choice['message']['content']

def response_anthropic(reply):
    content = reply['content'][0]
    return content['text']

##
## stream handlers
##

def stream_openai(chunk):
    return chunk['choices'][0]['delta'].get('content', '')

def stream_anthropic(chunk):
    if chunk['type'] == 'content_block_delta':
        return chunk['delta']['text']

def stream_oneping(chunk):
    return chunk

##
## native handlers
##

def response_openai_native(reply):
    return reply.choices[0].message.content

def response_anthropic_native(reply):
    return reply.content[0].text

def stream_openai_native(chunk):
    text = chunk.choices[0].delta.content
    if text is not None:
        return text
    else:
        return ''

def stream_anthropic_native(chunk):
    if chunk.type == 'content_block_delta':
        return chunk.delta.text
    else:
        return ''

##
## embedding handlers
##

def embed_payload_openai(text):
    return {'input': text}

def embed_response_openai(reply):
    return [
        item['embedding'] for item in reply['data']
    ]

def embed_response_openai_native(reply):
    return [
        item.embedding for item in reply.data
    ]

def embed_payload_tei(text):
    return {'inputs': text}

def embed_response_tei(reply):
    return reply

##
## tokenize handlers
##

def tokenize_payload_llamacpp(text):
    return {'content': text}

def tokenize_response_llamacpp(reply):
    return reply['tokens']

def tokenize_payload_tei(text):
    return {'inputs': text}

def tokenize_response_tei(reply):
    return [
        [ tk['id'] for tk in tokens ] for tokens in reply
    ]

def tokenize_payload_vllm(text):
    return {'prompt': text}

def tokenize_response_vllm(reply):
    return reply['tokens']

##
## transcribe handlers
##

def transcribe_response_openai(audio):
    return audio.text

##
## default handlers
##

HANDLERS = {
    'authorize': {
        'openai': authorize_openai,
        'anthropic': authorize_anthropic,
    },
    'content': {
        'openai': content_openai,
        'anthropic': content_anthropic,
        'oneping': content_oneping,
    },
    'payload': {
        'openai': payload_openai,
        'anthropic': payload_anthropic,
        'oneping': payload_oneping,
    },
    'response': {
        'openai': response_openai,
        'anthropic': response_anthropic,
        'oneping': response_oneping,
    },
    'stream': {
        'openai': stream_openai,
        'anthropic': stream_anthropic,
        'oneping': stream_oneping,
    },
    'embed_payload': {
        'openai': embed_payload_openai,
        'tei': embed_payload_tei,
    },
    'embed_response': {
        'openai': embed_response_openai,
        'tei': embed_response_tei,
    },
    'tokenize_payload': {
        'llama-cpp': tokenize_payload_llamacpp,
        'tei': tokenize_payload_tei,
        'vllm': tokenize_payload_vllm,
    },
    'tokenize_response': {
        'llama-cpp': tokenize_response_llamacpp,
        'tei': tokenize_response_tei,
        'vllm': tokenize_response_vllm,
    },
}

##
## known llm providers
##

# fault tolerant toml loader
def load_toml(file):
    if os.path.exists(file):
        return tomllib.load(file)
    else:
        return {}

# get config paths
XDG_LOC = os.path.expanduser('~/.config')
LIB_DIR = Path(__file__).parent
XDG_DIR = Path(os.environ.get('XDG_CONFIG_HOME', XDG_LOC))

# merge config layers
global PROVIDERS
global CONFIG
def reload():
    global PROVIDERS
    global CONFIG

    # reload config from disk
    DEFAULT_CONFIG = load_toml(LIB_DIR / 'config.toml')
    DEFAULT_PROVIDERS = load_toml(LIB_DIR / 'providers.toml')
    USER_CONFIG = load_toml(XDG_DIR / 'oneping' / 'config.toml')
    USER_PROVIDERS = load_toml(XDG_DIR / 'oneping' / 'providers.toml')

    # merge provider layers
    CONFIG = Config({ **DEFAULT_CONFIG, **USER_CONFIG })
    PROVIDERS = Config({
        p: Config({ **DEFAULT_PROVIDERS.get(p, {}), **USER_PROVIDERS.get(p, {}) })
        for p in [ *DEFAULT_PROVIDERS.keys(), *USER_PROVIDERS.keys() ]
    })
reload()

def get_provider(provider, **kwargs):
    # get full provider args
    if provider is None:
        provider = {}
    elif type(provider) is str:
        provider = PROVIDERS[provider]
    provider = {**PROVIDERS.default, **provider, **kwargs}

    # replace handler strings with functions
    for arg, handlers in HANDLERS.items():
        if arg in provider and type(pval := provider[arg]) is str:
            if pval not in handlers:
                raise ValueError(f'Invalid {arg} handler: {pval}')
            provider[arg] = handlers[pval]

    # return realized provider args
    return Config(provider)
