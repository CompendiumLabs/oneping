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
        reply as reply_anthropic,
        stream as stream_anthropic,
        reply_async as reply_async_anthropic,
        stream_async as stream_async_anthropic,
    )
except ImportError:
    dummy_anthropic = DummyFunction('anthropic')
    reply_anthropic = dummy_anthropic
    stream_anthropic = dummy_anthropic
    reply_async_anthropic = dummy_anthropic
    stream_async_anthropic = dummy_anthropic

##
## openai
##

try:
    from .openai import (
        reply as reply_openai,
        stream as stream_openai,
        reply_async as reply_async_openai,
        stream_async as stream_async_openai,
        embed as embed_openai,
    )
except ImportError:
    dummy_openai = DummyFunction('openai')
    reply_openai = dummy_openai
    stream_openai = dummy_openai
    reply_async_openai = dummy_openai
    stream_async_openai = dummy_openai
    embed_openai = dummy_openai

##
## fireworks
##

try:
    from .fireworks import (
        reply as reply_fireworks,
        stream as stream_fireworks,
        reply_async as reply_async_fireworks,
        stream_async as stream_async_fireworks,
    )
except ImportError:
    dummy_fireworks = DummyFunction('fireworks-ai')
    reply_fireworks = dummy_fireworks
    stream_fireworks = dummy_fireworks
    reply_async_fireworks = dummy_fireworks
    stream_async_fireworks = dummy_fireworks

##
## groq
##

try:
    from .groq import (
        reply as reply_groq,
        reply_async as reply_async_groq,
        stream as stream_groq,
        stream_async as stream_async_groq,
    )
except ImportError:
    dummy_groq = DummyFunction('groq')
    reply_groq = dummy_groq
    reply_async_groq = dummy_groq
    stream_groq = dummy_groq
    stream_async_groq = dummy_groq

##
## router
##

def reply(query, provider, **kwargs):
    if provider == 'openai':
        return reply_openai(query, **kwargs)
    elif provider == 'anthropic':
        return reply_anthropic(query, **kwargs)
    elif provider == 'fireworks':
        return reply_fireworks(query, **kwargs)
    elif provider == 'groq':
        return reply_groq(query, **kwargs)
    elif provider == 'local':
        raise Exception('Local provider does not support native requests')
    else:
        raise Exception(f'Provider {provider} not found')

def reply_async(query, provider, **kwargs):
    if provider == 'openai':
        return reply_async_openai(query, **kwargs)
    elif provider == 'anthropic':
        return reply_async_anthropic(query, **kwargs)
    elif provider == 'fireworks':
        return reply_async_fireworks(query, **kwargs)
    elif provider == 'groq':
        return reply_async_groq(query, **kwargs)
    elif provider == 'local':
        raise Exception('Local provider does not support native requests')
    else:
        raise Exception(f'Provider {provider} not found')

def stream(query, provider, **kwargs):
    if provider == 'openai':
        return stream_openai(query, **kwargs)
    elif provider == 'anthropic':
        return stream_anthropic(query, **kwargs)
    elif provider == 'fireworks':
        return stream_fireworks(query, **kwargs)
    elif provider == 'groq':
        return stream_groq(query, **kwargs)
    elif provider == 'local':
        raise Exception('Local provider does not support native requests')
    else:
        raise Exception(f'Provider {provider} not found')

def stream_async(query, provider, **kwargs):
    if provider == 'openai':
        return stream_async_openai(query, **kwargs)
    elif provider == 'anthropic':
        return stream_async_anthropic(query, **kwargs)
    elif provider == 'fireworks':
        return stream_async_fireworks(query, **kwargs)
    elif provider == 'groq':
        return stream_async_groq(query, **kwargs)
    elif provider == 'local':
        raise Exception('Local provider does not support native requests')
    else:
        raise Exception(f'Provider {provider} not found')

def embed(text, provider, **kwargs):
    if provider == 'openai':
        return embed_openai(text, **kwargs)
    elif provider == 'local':
        raise Exception('Local provider does not support native requests')
    else:
        raise Exception(f'Provider {provider} does not support embeddings')
