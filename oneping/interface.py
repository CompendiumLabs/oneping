# combined interface

from .curl import (
    reply as reply_url,
    stream as stream_url,
    stream_async as stream_async_url,
)
from .native import (
    reply as reply_native,
    stream as stream_native,
    stream_async as stream_async_native,
)

def reply(prompt, provider='local', native=False, **kwargs):
    if native:
        return reply_native(prompt, provider, **kwargs)
    else:
        return reply_url(prompt, provider=provider, **kwargs)

def stream(prompt, provider='local', native=False, **kwargs):
    if native:
        return stream_native(prompt, provider, **kwargs)
    else:
        return stream_url(prompt, provider=provider, **kwargs)

def stream_async(prompt, provider='local', native=False, **kwargs):
    if native:
        return stream_async_native(prompt, provider, **kwargs)
    else:
        return stream_async_url(prompt, provider=provider, **kwargs)
