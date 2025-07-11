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
        make_client as make_client_anthropic,
        reply as reply_anthropic,
        stream as stream_anthropic,
        reply_async as reply_async_anthropic,
        stream_async as stream_async_anthropic,
    )
except ImportError:
    dummy_anthropic = DummyFunction('anthropic')
    make_client_anthropic = dummy_anthropic
    reply_anthropic = dummy_anthropic
    stream_anthropic = dummy_anthropic
    reply_async_anthropic = dummy_anthropic
    stream_async_anthropic = dummy_anthropic

##
## openai
##

try:
    from .openai import (
        make_client as make_client_openai,
        reply as reply_openai,
        stream as stream_openai,
        reply_async as reply_async_openai,
        stream_async as stream_async_openai,
        embed as embed_openai,
        transcribe as transcribe_openai,
    )
except ImportError:
    dummy_openai = DummyFunction('openai')
    make_client_openai = dummy_openai
    reply_openai = dummy_openai
    stream_openai = dummy_openai
    reply_async_openai = dummy_openai
    stream_async_openai = dummy_openai
    embed_openai = dummy_openai
    transcribe_openai = dummy_openai
##
## fireworks
##

try:
    from .fireworks import (
        make_client as make_client_fireworks,
        reply as reply_fireworks,
        stream as stream_fireworks,
        reply_async as reply_async_fireworks,
        stream_async as stream_async_fireworks,
    )
except ImportError:
    dummy_fireworks = DummyFunction('fireworks-ai')
    make_client_fireworks = dummy_fireworks
    reply_fireworks = dummy_fireworks
    stream_fireworks = dummy_fireworks
    reply_async_fireworks = dummy_fireworks
    stream_async_fireworks = dummy_fireworks

##
## groq
##

try:
    from .groq import (
        make_client as make_client_groq,
        reply as reply_groq,
        reply_async as reply_async_groq,
        stream as stream_groq,
        stream_async as stream_async_groq,
    )
except ImportError:
    dummy_groq = DummyFunction('groq')
    make_client_groq = dummy_groq
    reply_groq = dummy_groq
    reply_async_groq = dummy_groq
    stream_groq = dummy_groq
    stream_async_groq = dummy_groq

##
## azure
##

try:
    from .azure import (
        make_client as make_client_azure,
        reply as reply_azure,
        reply_async as reply_async_azure,
        stream as stream_azure,
        stream_async as stream_async_azure,
        embed as embed_azure,
        transcribe as transcribe_azure,
    )
except ImportError as e:
    dummy_azure = DummyFunction('openai')
    make_client_azure = dummy_azure
    reply_azure = dummy_azure
    reply_async_azure = dummy_azure
    stream_azure = dummy_azure
    stream_async_azure = dummy_azure
    embed_azure = dummy_azure
    transcribe_azure = dummy_azure

##
## google
##

try:
    from .google import (
        make_client as make_client_google,
        reply as reply_google,
        stream as stream_google,
        reply_async as reply_async_google,
        stream_async as stream_async_google,
    )
except ImportError:
    dummy_google = DummyFunction('google')
    make_client_google = dummy_google
    reply_google = dummy_google
    stream_google = dummy_google
    reply_async_google = dummy_google
    stream_async_google = dummy_google

##
## xai
##

try:
    from .xai import (
        make_client as make_client_xai,
        reply as reply_xai,
        stream as stream_xai,
        reply_async as reply_async_xai,
        stream_async as stream_async_xai,
    )
except ImportError:
    dummy_xai = DummyFunction('xai')
    make_client_xai = dummy_xai
    reply_xai = dummy_xai
    stream_xai = dummy_xai
    reply_async_xai = dummy_xai
    stream_async_xai = dummy_xai

##
## router
##

def make_client(provider, **kwargs):
    if provider == 'openai':
        return make_client_openai(**kwargs)
    elif provider == 'anthropic':
        return make_client_anthropic(**kwargs)
    elif provider == 'fireworks':
        return make_client_fireworks(**kwargs)
    elif provider == 'groq':
        return make_client_groq(**kwargs)
    elif provider == 'azure':
        return make_client_azure(**kwargs)
    elif provider == 'google':
        return make_client_google(**kwargs)
    elif provider == 'xai':
        return make_client_xai(**kwargs)
    elif provider == 'local':
        raise Exception('Local provider does not support native requests')
    else:
        raise Exception(f'Provider {provider} not found')

def reply(query, provider, port=None, **kwargs):
    if provider == 'openai':
        return reply_openai(query, **kwargs)
    elif provider == 'anthropic':
        return reply_anthropic(query, **kwargs)
    elif provider == 'fireworks':
        return reply_fireworks(query, **kwargs)
    elif provider == 'groq':
        return reply_groq(query, **kwargs)
    elif provider == 'azure':
        return reply_azure(query, **kwargs)
    elif provider == 'google':
        return reply_google(query, **kwargs)
    elif provider == 'xai':
        return reply_xai(query, **kwargs)
    elif provider == 'local':
        raise Exception('Local provider does not support native requests')
    else:
        raise Exception(f'Provider {provider} not found')

def reply_async(query, provider, port=None, **kwargs):
    if provider == 'openai':
        return reply_async_openai(query, **kwargs)
    elif provider == 'anthropic':
        return reply_async_anthropic(query, **kwargs)
    elif provider == 'fireworks':
        return reply_async_fireworks(query, **kwargs)
    elif provider == 'groq':
        return reply_async_groq(query, **kwargs)
    elif provider == 'azure':
        return reply_async_azure(query, **kwargs)
    elif provider == 'google':
        return reply_async_google(query, **kwargs)
    elif provider == 'local':
        raise Exception('Local provider does not support native requests')
    else:
        raise Exception(f'Provider {provider} not found')

def stream(query, provider, port=None, **kwargs):
    if provider == 'openai':
        return stream_openai(query, **kwargs)
    elif provider == 'anthropic':
        return stream_anthropic(query, **kwargs)
    elif provider == 'fireworks':
        return stream_fireworks(query, **kwargs)
    elif provider == 'groq':
        return stream_groq(query, **kwargs)
    elif provider == 'azure':
        return stream_azure(query, **kwargs)
    elif provider == 'google':
        return stream_google(query, **kwargs)
    elif provider == 'xai':
        return stream_xai(query, **kwargs)
    elif provider == 'local':
        raise Exception('Local provider does not support native requests')
    else:
        raise Exception(f'Provider {provider} not found')

def stream_async(query, provider, port=None, **kwargs):
    if provider == 'openai':
        return stream_async_openai(query, **kwargs)
    elif provider == 'anthropic':
        return stream_async_anthropic(query, **kwargs)
    elif provider == 'fireworks':
        return stream_async_fireworks(query, **kwargs)
    elif provider == 'groq':
        return stream_async_groq(query, **kwargs)
    elif provider == 'azure':
        return stream_async_azure(query, **kwargs)
    elif provider == 'google':
        return stream_async_google(query, **kwargs)
    elif provider == 'xai':
        return stream_async_xai(query, **kwargs)
    elif provider == 'local':
        raise Exception('Local provider does not support native requests')
    else:
        raise Exception(f'Provider {provider} not found')

def embed(text, provider, port=None, **kwargs):
    if provider == 'openai':
        return embed_openai(text, **kwargs)
    elif provider == 'azure':
        return embed_azure(text, **kwargs)
    elif provider == 'local':
        raise Exception('Local provider does not support native requests')
    else:
        raise Exception(f'Provider {provider} does not support embeddings')

def transcribe(audio, provider, port=None, **kwargs):
    if provider == 'openai':
        return transcribe_openai(audio, **kwargs)
    elif provider == 'azure':
        return transcribe_azure(audio, **kwargs)
    elif provider == 'local':
        raise Exception('Local provider does not support native requests')
    else:
        raise Exception(f'Provider {provider} does not support transcribing')
