# combined interface

from .curl import (
    reply as reply_url,
    reply_async as reply_async_url,
    stream as stream_url,
    stream_async as stream_async_url,
    embed as embed_url,
)
from .native import (
    reply as reply_native,
    reply_async as reply_async_native,
    stream as stream_native,
    stream_async as stream_async_native,
    embed as embed_native,
    transcribe as transcribe_native,
)

def has_native(provider):
    return provider not in ('local', 'oneping')

def reply(query, provider='local', native=True, **kwargs):
    if native and has_native(provider):
        return reply_native(query, provider, **kwargs)
    else:
        return reply_url(query, provider=provider, **kwargs)

def reply_async(query, provider='local', native=True, **kwargs):
    if native and has_native(provider):
        return reply_async_native(query, provider, **kwargs)
    else:
        return reply_async_url(query, provider=provider, **kwargs)

def stream(query, provider='local', native=True, **kwargs):
    if native and has_native(provider):
        return stream_native(query, provider, **kwargs)
    else:
        return stream_url(query, provider=provider, **kwargs)

def stream_async(query, provider='local', native=True, **kwargs):
    if native and has_native(provider):
        return stream_async_native(query, provider, **kwargs)
    else:
        return stream_async_url(query, provider=provider, **kwargs)

def embed(text, provider='local', native=True, **kwargs):
    if native and has_native(provider):
        return embed_native(text, provider, **kwargs)
    else:
        return embed_url(text, provider=provider, **kwargs)

def transcribe(audio, provider='local', native=True, **kwargs):
    if native and has_native(provider):
        return transcribe_native(audio, provider, **kwargs)
    else:
        raise Exception('Transcribing is not supported for non-native providers')
