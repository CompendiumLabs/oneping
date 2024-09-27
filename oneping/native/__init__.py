# native library interfaces

##
## dummy function
##

class DummyFunction:
    def __init__(self, package):
        self.package = package

    def __call__(self, *args, **kwargs):
        raise Exception(f'Please install package: {self.package}')

##
## anthropic
##

try:
    from .anthropic import (
        get_llm_response as get_anthropic_response,
        stream_llm_response as stream_anthropic_response,
        async_llm_response as async_anthropic_response,
    )
except ImportError:
    dummy_anthropic = DummyFunction('anthropic')
    get_anthropic_response = dummy_anthropic
    stream_anthropic_response = dummy_anthropic
    async_anthropic_response = dummy_anthropic

##
## openai
##

try:
    from .openai import (
        get_llm_response as get_openai_response,
        stream_llm_response as stream_openai_response,
        async_llm_response as async_openai_response,
        get_embed_response as get_openai_embed_response,
    )
except ImportError:
    dummy_openai = DummyFunction('openai')
    get_openai_response = dummy_openai
    stream_openai_response = dummy_openai
    async_openai_response = dummy_openai
    get_openai_embed_response = dummy_openai

##
## fireworks
##

try:
    from .fireworks import (
        get_llm_response as get_fireworks_response,
        stream_llm_response as stream_fireworks_response,
        async_llm_response as async_fireworks_response,
    )
except ImportError:
    dummy_fireworks = DummyFunction('fireworks-ai')
    get_fireworks_response = dummy_fireworks
    stream_fireworks_response = dummy_fireworks
    async_fireworks_response = dummy_fireworks

##
## groq
##

try:
    from .groq import (
        get_llm_response as get_groq_response,
        stream_llm_response as stream_groq_response,
        async_llm_response as async_groq_response,
    )
except ImportError:
    dummy_groq = DummyFunction('groq')
    get_groq_response = dummy_groq
    stream_groq_response = dummy_groq
    async_groq_response = dummy_groq

##
## router
##

def reply(prompt, provider, **kwargs):
    if provider == 'openai':
        return get_openai_response(prompt, **kwargs)
    elif provider == 'anthropic':
        return get_anthropic_response(prompt, **kwargs)
    elif provider == 'fireworks':
        return get_fireworks_response(prompt, **kwargs)
    elif provider == 'groq':
        return get_groq_response(prompt, **kwargs)
    elif provider == 'local':
        raise Exception('Local provider does not support native requests')
    else:
        raise Exception(f'Provider {provider} not found')

def stream(prompt, provider, **kwargs):
    if provider == 'openai':
        return stream_openai_response(prompt, **kwargs)
    elif provider == 'anthropic':
        return stream_anthropic_response(prompt, **kwargs)
    elif provider == 'fireworks':
        return stream_fireworks_response(prompt, **kwargs)
    elif provider == 'groq':
        return stream_groq_response(prompt, **kwargs)
    elif provider == 'local':
        raise Exception('Local provider does not support native requests')
    else:
        raise Exception(f'Provider {provider} not found')

def stream_async(prompt, provider, **kwargs):
    if provider == 'openai':
        return async_openai_response(prompt, **kwargs)
    elif provider == 'anthropic':
        return async_anthropic_response(prompt, **kwargs)
    elif provider == 'fireworks':
        return async_fireworks_response(prompt, **kwargs)
    elif provider == 'groq':
        return async_groq_response(prompt, **kwargs)
    elif provider == 'local':
        raise Exception('Local provider does not support native requests')
    else:
        raise Exception(f'Provider {provider} not found')

def embed(text, provider, **kwargs):
    if provider == 'openai':
        return get_openai_embed_response(text, **kwargs)
    else:
        raise Exception(f'Provider {provider} does not support embeddings')
