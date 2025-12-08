import sys
import fire

from .utils import streamer, load_image_uri
from .api import reply, stream, embed
from .server import start_llama_cpp, start_router

def get_content(query=None, image=None):
    # get query/image from stdin
    if query is None or query == '-':
        if not sys.stdin.isatty():
            query = sys.stdin.read()
    if image == '-':
        if not sys.stdin.isatty():
            image = sys.stdin.read()

    # return content dict
    content = {}
    if query is not None:
        content['query'] = query
    if image is not None:
        content['image'] = load_image_uri(image)
    return content

class ChatCLI:
    def reply(self, query=None, image=None, **kwargs):
        content = get_content(query, image)
        return reply(**content, **kwargs)

    def stream(self, query=None, image=None, **kwargs):
        content = get_content(query, image)
        reply = stream(**content, **kwargs)
        streamer(reply)
        print()

    def embed(self, text=None, **kwargs):
        content = get_content(text)
        return embed(**content, **kwargs)

    def console(self, **kwargs):
        from .interface.textual import main as main_textual
        main_textual(**kwargs)

    def prompt(self, **kwargs):
        from .interface.prompt import main as main_prompt
        main_prompt(**kwargs)

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
