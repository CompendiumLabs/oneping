# default arguments

import os

from .utils import parse_image_uri

##
## system prompt
##

DEFAULT_SYSTEM = os.environ.get('ONEPING_SYSTEM', None)
DEFAULT_MAX_TOKENS = int(os.environ.get('ONEPING_MAX_TOKENS', 2048))

##
## models
##

OPENAI_MODEL = 'gpt-5'
OPENAI_EMBED = 'text-embedding-3-large'
OPENAI_TRANSCRIBE = 'gpt-5-transcribe'
ANTHROPIC_MODEL = 'claude-opus-4-1-20250805'
FIREWORKS_MODEL = 'accounts/fireworks/models/llama-v3p3-70b-instruct'
GROQ_MODEL = 'llama-3.3-70b-versatile'
DEEPSEEK_MODEL = 'deepseek-chat'
GOOGLE_MODEL = 'gemini-2.0-flash-exp'
GOOGLE_EMBED = 'gemini-embedding-exp-03-07'
XAI_MODEL = 'grok-4'

##
## environment key names
##

OPENAI_KEYENV = 'OPENAI_API_KEY'
ANTHROPIC_KEYENV = 'ANTHROPIC_API_KEY'
FIREWORKS_KEYENV = 'FIREWORKS_API_KEY'
GROQ_KEYENV = 'GROQ_API_KEY'
DEEPSEEK_KEYENV = 'DEEPSEEK_API_KEY'
AZURE_KEYENV = 'AZURE_OPENAI_API_KEY'
GOOGLE_KEYENV = 'GEMINI_API_KEY'
XAI_KEYENV = 'XAI_API_KEY'

##
## options
##

AZURE_API_VERSION = '2024-10-21'
ANTHROPIC_HEADERS = {
    'anthropic-version': '2023-06-01',
}

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
## content converters
##

def content_openai(text, image=None):
    if image is None:
        return text
    image_url = { 'url': image }
    return [
        { 'type': 'image_url', 'image_url': image_url },
        { 'type': 'text', 'text': text },
    ]

def content_anthropic(text, image=None):
    if image is None:
        return text
    media_type, data = parse_image_uri(image)
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
## known llm providers
##

DEFAULT_PROVIDER = 'llama.cpp'

DEFAULT_PROVIDER_ARGS = {
    'authorize': None,
    'base_url': 'http://localhost:8080',
    'chat_path': 'v1/chat/completions',
    'embed_path': 'v1/embeddings',
    'tokenize_path': 'tokenize',
    'content': content_openai,
    'payload': payload_openai,
    'response': response_openai,
    'stream': stream_openai,
    'embed_payload': embed_payload_openai,
    'embed_response': embed_response_openai,
}

# presets for known llm providers
LLM_PROVIDERS = {
    'llama.cpp': {
        'tokenize_payload': tokenize_payload_llamacpp,
        'tokenize_response': tokenize_response_llamacpp,
    },
    'tei': {
        'embed_path': 'embed',
        'embed_payload': embed_payload_tei,
        'embed_response': embed_response_tei,
        'tokenize_payload': tokenize_payload_tei,
        'tokenize_response': tokenize_response_tei,
    },
    'vllm': {
        'tokenize_payload': tokenize_payload_vllm,
        'tokenize_response': tokenize_response_vllm,
    },
    'oneping': {
        'chat_path': 'chat',
        'embed_path': 'embed',
        'tokenize_path': 'tokenize',
        'max_tokens_name': 'max_tokens',
        'content': content_oneping,
        'payload': payload_oneping,
        'response': response_oneping,
        'stream': stream_oneping,
    },
    'openai': {
        'base_url': 'https://api.openai.com/v1',
        'api_key_env': OPENAI_KEYENV,
        'chat_model': OPENAI_MODEL,
        'embed_model': OPENAI_EMBED,
    },
    'anthropic': {
        'base_url': 'https://api.anthropic.com/v1',
        'chat_path': 'messages',
        'max_tokens_name': 'max_tokens',
        'content': content_anthropic,
        'payload': payload_anthropic,
        'authorize': authorize_anthropic,
        'response': response_anthropic,
        'stream': stream_anthropic,
        'api_key_env': ANTHROPIC_KEYENV,
        'chat_model': ANTHROPIC_MODEL,
        'headers': ANTHROPIC_HEADERS,
    },
    'google': {
        'base_url': 'https://generativelanguage.googleapis.com/v1beta/openai',
        'api_key_env': GOOGLE_KEYENV,
        'chat_model': GOOGLE_MODEL,
        'embed_model': GOOGLE_EMBED,
    },
    'xai': {
        'base_url': 'https://api.x.ai/v1',
        'api_key_env': XAI_KEYENV,
        'chat_model': XAI_MODEL,
    },
    'fireworks': {
        'base_url': 'https://api.fireworks.ai/inference',
        'api_key_env': FIREWORKS_KEYENV,
        'chat_model': FIREWORKS_MODEL,
    },
    'groq': {
        'base_url': 'https://api.groq.com/openai',
        'api_key_env': GROQ_KEYENV,
        'chat_model': GROQ_MODEL,
    },
    'deepseek': {
        'base_url': 'https://api.deepseek.com',
        'api_key_env': DEEPSEEK_KEYENV,
        'chat_model': DEEPSEEK_MODEL,
    },
}

def get_provider(provider):
    if type(provider) is str:
        provider = LLM_PROVIDERS[provider]
    return {**DEFAULT_PROVIDER_ARGS, **provider}
