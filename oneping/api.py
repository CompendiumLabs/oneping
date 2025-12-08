# combined interface

from .native import has_native

from .curl import (
    reply as reply_url,
    reply_async as reply_async_url,
    stream as stream_url,
    stream_async as stream_async_url,
    embed as embed_url,
    tokenize as tokenize_url,
)
from .native import (
    reply as reply_native,
    reply_async as reply_async_native,
    stream as stream_native,
    stream_async as stream_async_native,
    embed as embed_native,
    tokenize as tokenize_native,
    transcribe as transcribe_native,
)

def reply(query, provider=None, native=True, **kwargs):
    if native and has_native(provider):
        return reply_native(query, provider, **kwargs)
    else:
        return reply_url(query, provider=provider, **kwargs)

def reply_async(query, provider=None, native=True, **kwargs):
    if native and has_native(provider):
        return reply_async_native(query, provider, **kwargs)
    else:
        return reply_async_url(query, provider=provider, **kwargs)

def stream(query, provider=None, native=True, **kwargs):
    if native and has_native(provider):
        return stream_native(query, provider, **kwargs)
    else:
        return stream_url(query, provider=provider, **kwargs)

def stream_async(query, provider=None, native=True, **kwargs):
    if native and has_native(provider):
        return stream_async_native(query, provider, **kwargs)
    else:
        return stream_async_url(query, provider=provider, **kwargs)

def embed(text, provider=None, native=True, **kwargs):
    if native and has_native(provider):
        return embed_native(text, provider, **kwargs)
    else:
        return embed_url(text, provider=provider, **kwargs)

def tokenize(text, provider=None, native=True, **kwargs):
    if native and has_native(provider):
        return tokenize_native(text, provider, **kwargs)
    else:
        return tokenize_url(text, provider=provider, **kwargs)

def transcribe(audio, provider=None, native=True, **kwargs):
    if native and has_native(provider):
        return transcribe_native(audio, provider, **kwargs)
    else:
        raise Exception('Transcribing is not supported for non-native providers')
