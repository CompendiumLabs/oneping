import sys
import fire

from .utils import streamer
from .interface import reply, stream, embed
from .chat import chat_textual, chat_fasthtml
from .server import start as start_server

def get_prompt(prompt):
    if prompt is None:
        if not sys.stdin.isatty():
            prompt = sys.stdin.read()
    return prompt

class ChatCLI:
    def reply(self, prompt=None, **kwargs):
        prompt = get_prompt(prompt)
        if prompt is None:
            return 'No prompt specified'
        return reply(prompt, **kwargs)

    def stream(self, prompt=None, **kwargs):
        prompt = get_prompt(prompt)
        if prompt is None:
            return 'No prompt specified'
        reply = stream(prompt, **kwargs)
        streamer(reply)
        print()

    def embed(self, text=None, **kwargs):
        text = get_prompt(text)
        if text is None:
            return 'No text specified'
        return embed(text, **kwargs)

    def console(self, **kwargs):
        chat_textual(**kwargs)

    def web(self, **kwargs):
        chat_fasthtml(**kwargs)

    def server(self, model, **kwargs):
        start_server(model, **kwargs)

def main():
    fire.Fire(ChatCLI)

if __name__ == '__main__':
    main()
