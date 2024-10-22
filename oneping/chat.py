# chat interface

from .providers import DEFAULT_SYSTEM
from .api import reply, reply_async, stream, stream_async

# chat interface
class Chat:
    def __init__(self, system=None, **kwargs):
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
            query, system=self.system, history=self.history, **self.kwargs, **kwargs
        )

        # return text
        return text

    async def reply_async(self, query, **kwargs):
        # get full history and text
        self.history, text = await reply_async(
            query, system=self.system, history=self.history, **self.kwargs, **kwargs
        )

        # return text
        return text

    def stream(self, query, **kwargs):
        # get input history (plus prefill) and stream
        replies = stream(
            query, system=self.system, history=self.history, **self.kwargs, **kwargs
        )

        # yield text stream
        reply = ''
        for chunk in replies:
            yield chunk
            reply += chunk

        # update final history (reply includes prefill)
        self.history += [
            {'role': 'user'     , 'content': query},
            {'role': 'assistant', 'content': reply},
        ]

    async def stream_async(self, query, **kwargs):
        # get input history (plus prefill) and stream
        replies = stream_async(
            query, system=self.system, history=self.history, **self.kwargs, **kwargs
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
