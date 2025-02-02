# default arguments

##
## models
##

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

##
## environment key names
##

OPENAI_KEYENV = 'OPENAI_API_KEY'
ANTHROPIC_KEYENV = 'ANTHROPIC_API_KEY'
FIREWORKS_KEYENV = 'FIREWORKS_API_KEY'
GROQ_KEYENV = 'GROQ_API_KEY'
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

def payload_openai(query=None, system=None, prefill=None, prediction=None, history=None):
    if system is not None:
        messages = [{'role': 'system', 'content': system}]
    else:
        messages = []
    if type(history) is list:
        messages += history
    if query is not None:
        messages.append({'role': 'user', 'content': query})
    if prefill is not None:
        messages.append({'role': 'assistant', 'content': prefill})
    payload = {'messages': messages}
    if prediction is not None:
        payload['prediction'] = {'type': 'content', 'content': prediction}
    return payload

def payload_anthropic(query=None, system=None, prefill=None, prediction=None, history=None):
    if type(history) is list:
        messages = [*history]
    else:
        messages = []
    if query is not None:
        messages.append({'role': 'user', 'content': query})
    if prefill is not None:
        messages.append({'role': 'assistant', 'content': prefill})
    payload = {'messages': messages}
    if system is not None:
        payload['system'] = system
    return payload

##
## response extraction
##

def response_openai(reply):
    choice = reply['choices'][0]
    return choice['message']['content']

def response_anthropic(reply):
    content = reply['content'][0]
    return content['text']

def stream_openai(chunk):
    return chunk['choices'][0]['delta'].get('content', '')

def stream_anthropic(chunk):
    if chunk['type'] == 'content_block_delta':
        return chunk['delta']['text']
    else:
        return ''

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

def embed_openai(reply):
    return reply['data'][0]['embedding']

def transcribe_openai(audio):
    return audio.text

##
## known llm providers
##

DEFAULT_PROVIDER = {
    'authorize': authorize_openai,
    'payload': payload_openai,
    'response': response_openai,
    'stream': stream_openai,
    'embed': embed_openai,
}

# presets for known llm providers
LLM_PROVIDERS = {
    'local': {
        'url': 'http://localhost:{port}/v1/chat/completions',
        'authorize': None,
    },
    'openai': {
        'url': 'https://api.openai.com/v1/chat/completions',
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
        'api_key_env': FIREWORKS_KEYENV,
        'model': FIREWORKS_MODEL,
    },
    'groq': {
        'url': 'https://api.groq.com/openai/v1/chat/completions',
        'api_key_env': GROQ_KEYENV,
        'model': GROQ_MODEL,
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
        'url': 'http://localhost:{port}/v1/embeddings',
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
