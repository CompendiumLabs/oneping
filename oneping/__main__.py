import sys
import fire

from .utils import streamer
from .interface import reply, stream, embed
from .chat import chat_textual, chat_fasthtml
from .server import start as start_server

def get_query(query):
    if query is None:
        if not sys.stdin.isatty():
            query = sys.stdin.read()
    return query

class ChatCLI:
    def reply(self, query=None, **kwargs):
        query = get_query(query)
        if query is None:
            return 'No query specified'
        return reply(query, **kwargs)

    def stream(self, query=None, **kwargs):
        query = get_query(query)
        if query is None:
            return 'No query specified'
        reply = stream(query, **kwargs)
        streamer(reply)
        print()

    def embed(self, text=None, **kwargs):
        text = get_query(text)
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
