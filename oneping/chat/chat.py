# chat interface

from ..providers import DEFAULT_SYSTEM
from ..interface import reply, stream, stream_async

# chat interface
class Chat:
    def __init__(self, provider='local', model=None, system=None, **kwargs):
        self.provider = provider
        self.model = model
        self.system = DEFAULT_SYSTEM if system is None else system
        self.kwargs = kwargs
        self.clear()

    def __call__(self, query, **kwargs):
        return self.reply(query, **kwargs)

    def clear(self):
        self.history = []

    def reply(self, query, **kwargs):
        # get full history and text
        self.history, text = reply(
            query, provider=self.provider, model=self.model, system=self.system,
            history=self.history, **self.kwargs, **kwargs
        )

        # return text
        return text

    async def stream_async(self, query, **kwargs):
        # get input history (plus prefill) and stream
        replies = stream_async(
            query, provider=self.provider, model=self.model, system=self.system,
            history=self.history, **self.kwargs, **kwargs
        )

        # yield text stream
        reply = ''
        async for chunk in replies:
            yield chunk
            reply += chunk

        # update final history (reply includes prefill)
        self.history += [
            {'role': 'user'     , 'content': query},
            {'role': 'assistant', 'content': reply },
        ]

    def stream(self, query, **kwargs):
        # get input history (plus prefill) and stream
        replies = stream(
            query, provider=self.provider, model=self.model, system=self.system,
            history=self.history, **self.kwargs, **kwargs
        )

        # yield text stream
        reply = ''
        for chunk in replies:
            yield chunk
            reply += chunk

        # update final history (reply includes prefill)
        self.history += [
            {'role': 'user'     , 'content': query},
            {'role': 'assistant', 'content': reply },
        ]

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
