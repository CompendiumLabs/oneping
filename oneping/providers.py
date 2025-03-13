# default arguments

import mimetypes
import base64

##
## system prompt
##

DEFAULT_SYSTEM = 'You are a helpful and knowledgeable AI assistant. Answer the queries provided to the best of your ability.'
DEFAULT_MAX_TOKENS = 1024

##
## models
##

OPENAI_MODEL = 'gpt-4o'
OPENAI_EMBED = 'text-embedding-3-small'
OPENAI_WHISPER = 'whisper-1'
ANTHROPIC_MODEL = 'claude-3-5-sonnet-latest'
FIREWORKS_MODEL = 'accounts/fireworks/models/llama-v3p1-70b-instruct'
GROQ_MODEL = 'llama-3.1-70b-versatile'
DEEPSEEK_MODEL = 'deepseek-chat'

##
## environment key names
##

OPENAI_KEYENV = 'OPENAI_API_KEY'
ANTHROPIC_KEYENV = 'ANTHROPIC_API_KEY'
FIREWORKS_KEYENV = 'FIREWORKS_API_KEY'
GROQ_KEYENV = 'GROQ_API_KEY'
DEEPSEEK_KEYENV = 'DEEPSEEK_API_KEY'
AZURE_KEYENV = 'AZURE_OPENAI_API_KEY'

##
## options
##

AZURE_API_VERSION = '2024-10-21'
ANTHROPIC_HEADERS = {
    'anthropic-version': '2023-06-01',
    'anthropic-beta': 'prompt-caching-2024-07-31',
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
## message payloads
##

def convert_image(image):
    with open(image, 'rb') as f:
        data = f.read()
    media_type, _ = mimetypes.guess_type(image)
    sdata = base64.b64encode(data).decode('utf-8')
    return {
        'type': 'base64', 'media_type': media_type, 'data': sdata
    }

def content_openai(text=None, image=None):
    contents = []
    if image is not None:
        contents.append({ 'type': 'image', 'source': convert_image(image) })
    if text is not None:
        contents.append({ 'type': 'text', 'text': text })
    return contents

def payload_oneping(content, system=None, prefill=None, prediction=None, history=None):
    return {
        'content': content,
        'system': system,
        'prefill': prefill,
        'prediction': prediction,
        'history': history,
    }

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
        payload['system'] = system
    return payload

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
## other modal handlers
##

def embed_openai(reply):
    return reply['data'][0]['embedding']

def transcribe_openai(audio):
    return audio.text

##
## known llm providers
##

DEFAULT_PROVIDER = {
    'content': content_openai,
    'payload': payload_openai,
    'response': response_openai,
    'stream': stream_openai,
    'embed': embed_openai,
}

# presets for known llm providers
LLM_PROVIDERS = {
    'local': {
        'url': 'http://{host}:{port}/v1/chat/completions',
        'host': 'localhost',
        'port': 8000,
    },
    'oneping': {
        'url': 'http://{host}:{port}/chat',
        'host': 'localhost',
        'port': 5000,
        'authorize': None,
        'payload': payload_oneping,
        'response': response_oneping,
        'stream': stream_oneping,
    },
    'openai': {
        'url': 'https://api.openai.com/v1/chat/completions',
        'authorize': authorize_openai,
        'max_tokens_name': 'max_completion_tokens',
        'api_key_env': OPENAI_KEYENV,
        'model': OPENAI_MODEL,
    },
    'anthropic': {
        'url': 'https://api.anthropic.com/v1/messages',
        'payload': payload_anthropic,
        'authorize': authorize_anthropic,
        'response': response_anthropic,
        'stream': stream_anthropic,
        'api_key_env': ANTHROPIC_KEYENV,
        'model': ANTHROPIC_MODEL,
        'headers': ANTHROPIC_HEADERS,
    },
    'fireworks': {
        'url': 'https://api.fireworks.ai/inference/v1/chat/completions',
        'authorize': authorize_openai,
        'api_key_env': FIREWORKS_KEYENV,
        'model': FIREWORKS_MODEL,
    },
    'groq': {
        'url': 'https://api.groq.com/openai/v1/chat/completions',
        'authorize': authorize_openai,
        'max_tokens_name': 'max_completion_tokens',
        'api_key_env': GROQ_KEYENV,
        'model': GROQ_MODEL,
    },
    'deepseek': {
        'url': 'https://api.deepseek.com/chat/completions',
        'authorize': authorize_openai,
        'api_key_env': DEEPSEEK_KEYENV,
        'model': DEEPSEEK_MODEL,
    },
}

def get_provider(provider):
    if type(provider) is str:
        provider = LLM_PROVIDERS[provider]
    return {**DEFAULT_PROVIDER, **provider}

##
## embedding providers
##

DEFAULT_EMBED = {
    'authorize': authorize_openai,
    'embed': embed_openai,
}

EMBED_PROVIDERS = {
    'local': {
        'url': 'http://{host}:{port}/v1/embeddings',
        'authorize': None,
    },
    'openai': {
        'url': 'https://api.openai.com/v1/embeddings',
        'api_key_env': 'OPENAI_API_KEY',
        'model': 'text-embedding-3-small',
    },
}

def get_embed_provider(provider):
    if type(provider) is str:
        provider = EMBED_PROVIDERS[provider]
    return {**DEFAULT_EMBED, **provider}
