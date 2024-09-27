import sys
import fire

from .utils import streamer
from .interface import reply, stream, embed
from .chat import chat_textual, chat_fasthtml
from .server import (
    start as start_server,
    embed as embed_server,
)

class ChatCLI:
    def __init__(
        self, provider='local', native=False, system=None, url=None, port=8000,
        api_key=None, model=None, max_tokens=1024, **kwargs
    ):
        self.kwargs = dict(
            provider=provider, native=native, system=system, url=url, port=port,
            api_key=api_key, model=model, max_tokens=max_tokens, **kwargs
        )

    def reply(self, prompt=None):
        if prompt is None:
            prompt = sys.stdin.read()
        return reply(prompt, **self.kwargs)

    def stream(self, prompt=None):
        if prompt is None:
            prompt = sys.stdin.read()
        reply = stream(prompt, **self.kwargs)
        streamer(reply)
        print()

    def embed(self, text=None):
        if text is None:
            text = sys.stdin.read()
        return embed(text, **self.kwargs)

    def console(self):
        chat_textual(**self.kwargs)

    def web(self, chat_host='127.0.0.1', chat_port=5000):
        chat_fasthtml(chat_host=chat_host, chat_port=chat_port, **self.kwargs)

    def server(self, model, host='127.0.0.1', **kwargs):
        port = self.kwargs['port']
        start_server(model, host=host, port=port, **kwargs)

    def server_embed(self, model, host='127.0.0.1', **kwargs):
        port = self.kwargs['port']
        embed_server(model, host=host, port=port, **kwargs)

if __name__ == '__main__':
    fire.Fire(ChatCLI)
