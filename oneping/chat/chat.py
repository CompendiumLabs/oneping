# chat interface to curl
# https://textual.textualize.io/blog/2024/09/15/anatomy-of-a-textual-user-interface/

from ..default import SYSTEM, syncify
from ..curl import LLM_PROVIDERS, get_llm_response, async_llm_response, compose_history

# chat interface
class Chat:
    def __init__(self, provider='local', system=None, **kwargs):
        self.provider = provider
        self.system = SYSTEM if system is None else system
        self.kwargs = kwargs
        self.clear()

    def __call__(self, prompt, **kwargs):
        return self.chat(prompt, **kwargs)

    def clear(self):
        self.history = []

    def chat(self, prompt, **kwargs):
        # get full history and text
        self.history, text = get_llm_response(
            prompt, provider=self.provider, history=self.history, system=self.system, **self.kwargs, **kwargs
        )

        # return text
        return text

    async def stream_async(self, prompt, **kwargs):
        # get input history (plus prefill) and stream
        replies = async_llm_response(
            prompt, provider=self.provider, history=self.history, system=self.system, **self.kwargs, **kwargs
        )

        # yield text stream
        reply = ''
        async for chunk in replies:
            yield chunk
            reply += chunk

        # update final history (reply includes prefill)
        self.history += [
            {'role': 'user'     , 'content': prompt},
            {'role': 'assistant', 'content': reply },
        ]

    def stream(self, prompt, **kwargs):
        return syncify(self.stream_async(prompt, **kwargs))

# textual powered chat interface
def chat_textual(provider='local', **kwargs):
    from .textual import TextualChat
    chat = Chat(provider=provider, **kwargs)
    app = TextualChat(chat)
    app.run()

# fasthtml powered chat interface
def chat_fasthtml(provider='local', chat_host='127.0.0.1', chat_port=5000, reload=False, **kwargs):
    import uvicorn
    from fasthtml.common import serve
    from .fasthtml import FastHTMLChat

    # make application
    chat = Chat(provider=provider, **kwargs)
    app = FastHTMLChat(chat)

    # run server
    config = uvicorn.Config(app, host=chat_host, port=chat_port, reload=reload)
    server = uvicorn.Server(config)
    server.run()
