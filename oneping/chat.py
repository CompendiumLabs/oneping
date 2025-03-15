# chat interface

from .providers import DEFAULT_SYSTEM
from .api import reply, reply_async, stream, stream_async

def history_update(query, text, image=None):
    # make user message
    user_content = {'text': query}
    if image is not None:
        user_content['image'] = image
    user = { 'role': 'user', 'content': user_content }

    # make assistant message
    asst_content = {'text': text }
    assistant = { 'role': 'assistant', 'content': asst_content }

    # return history
    return [user, assistant]

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

    def reply(self, query, image=None, **kwargs):
        # get full history and text
        text = reply(
            query, image=image, system=self.system, history=self.history, **self.kwargs, **kwargs
        )

        # update history
        self.history += history_update(query, text, image)

        # return text
        return text

    async def reply_async(self, query, image=None, **kwargs):
        # get full history and text
        text = await reply_async(
            query, image=image, system=self.system, history=self.history, **self.kwargs, **kwargs
        )

        # update history
        self.history += history_update(query, text, image)

        # return text
        return text

    def stream(self, query, image=None, **kwargs):
        # get input history (plus prefill) and stream
        replies = stream(
            query, image=image, system=self.system, history=self.history, **self.kwargs, **kwargs
        )

        # yield text stream
        reply = ''
        for chunk in replies:
            yield chunk
            reply += chunk

        # update final history (reply includes prefill)
        self.history += history_update(query, reply, image)

    async def stream_async(self, query, image=None, **kwargs):
        # get input history (plus prefill) and stream
        replies = stream_async(
            query, image=image, system=self.system, history=self.history, **self.kwargs, **kwargs
        )

        # yield text stream
        reply = ''
        async for chunk in replies:
            yield chunk
            reply += chunk

        # update final history (reply includes prefill)
        self.history += history_update(query, reply, image)
