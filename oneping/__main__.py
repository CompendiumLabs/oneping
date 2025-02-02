import sys
import fire

from .utils import streamer
from .api import reply, stream, embed
from .server import start_llama_cpp, start_router

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
        from .interface.textual import main as main_textual
        main_textual(**kwargs)

    def web(self, **kwargs):
        from .interface.fasthtml import main as main_fasthtml
        main_fasthtml(**kwargs)

    def server(self, model, **kwargs):
        start_llama_cpp(model, **kwargs)

    def router(self, **kwargs):
        start_router(**kwargs)

def main():
    fire.Fire(ChatCLI)

if __name__ == '__main__':
    main()
