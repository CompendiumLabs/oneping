import sys
import fire

from .utils import streamer
from .interface import reply, stream, embed
from .chat import chat_textual, chat_fasthtml
from .server import start as start_server

class ChatCLI:
    def reply(self, prompt=None, **kwargs):
        if prompt is None:
            prompt = sys.stdin.read()
        return reply(prompt, **kwargs)

    def stream(self, prompt=None, **kwargs):
        if prompt is None:
            prompt = sys.stdin.read()
        reply = stream(prompt, **kwargs)
        streamer(reply)
        print()

    def embed(self, text=None, **kwargs):
        if text is None:
            text = sys.stdin.read()
        return embed(text, **kwargs)

    def console(self, **kwargs):
        chat_textual(**kwargs)

    def web(self, **kwargs):
        chat_fasthtml(**kwargs)

    def server(self, model, **kwargs):
        start_server(model, **kwargs)

if __name__ == '__main__':
    fire.Fire(ChatCLI)
