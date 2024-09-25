import sys
import fire

from .default import streamer
from .curl import get_llm_response, stream_llm_response
from .chat import chat_textual, chat_fasthtml

class ChatCLI:
    def __init__(
        self, provider='local', system=None, url=None, port=8000, api_key=None, model=None, max_tokens=1024,
        chat_host='127.0.0.1', chat_port=5000, **kwargs
    ):
        self.chat_host = chat_host
        self.chat_port = chat_port
        self.kwargs = dict(
            provider=provider, system=system, url=url, port=port, api_key=api_key, model=model,
            max_tokens=max_tokens, **kwargs
        )

    def reply(self, prompt=None):
        if prompt is None:
            prompt = sys.stdin.read()
        return get_llm_response(prompt, **self.kwargs)

    async def stream(self, prompt=None):
        if prompt is None:
            prompt = sys.stdin.read()
        stream = stream_llm_response(prompt, **self.kwargs)
        await streamer(stream)
        print()

    def console(self):
        chat_textual(chat_host=self.chat_host, chat_port=self.chat_port, **self.kwargs)

    def web(self):
        chat_fasthtml(chat_host=self.chat_host, chat_port=self.chat_port, **self.kwargs)

if __name__ == '__main__':
    fire.Fire(ChatCLI)
