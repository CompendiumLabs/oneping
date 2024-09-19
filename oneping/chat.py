# chat interface to curl
# https://textual.textualize.io/blog/2024/09/15/anatomy-of-a-textual-user-interface/

from .default import SYSTEM
from .curl import LLM_PROVIDERS, get_llm_response, stream_llm_response, compose_history

# stream printer
def sprint(s):
    print(s, end='', flush=True)

async def cumcat(stream):
    reply = ''
    async for chunk in stream:
        reply += chunk
        yield reply

# chat interface
class Chat:
    def __init__(self, provider='local', system=None, **kwargs):
        self.provider = provider
        self.system = SYSTEM if system is None else system
        self.kwargs = kwargs

        # set up initial history (either [] or [system])
        payload = LLM_PROVIDERS[provider]['payload']
        self.history = payload(system=self.system)['messages']

    def __call__(self, prompt, **kwargs):
        return self.chat(prompt, **kwargs)

    def chat(self, prompt, **kwargs):
        # get full history and text
        self.history, text = get_llm_response(
            prompt, provider=self.provider, history=self.history, system=self.system, **self.kwargs, **kwargs
        )

        # return text
        return text

    async def stream(self, prompt, **kwargs):
        # get input history (plus prefill) and stream
        replies = stream_llm_response(
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

# colors
role_colors = {
    'system': '#4caf50',
    'user': '#1e88e5',
    'assistant': '#ff0d57',
}

# textualize powered chat interface
def main(provider='local', **kwargs):
    from textual import on, work
    from textual.app import App, ComposeResult
    from textual.widget import Widget
    from textual.widgets import Header, Input, Static, Markdown
    from textual.containers import VerticalScroll
    from textual.events import Key
    from textual.reactive import reactive
    from rich.style import Style
    from rich.text import Text
    from rich.panel import Panel

    # make chat history
    chat = Chat(provider=provider, **kwargs)

    class ChatMessage(Markdown):
        def __init__(self, title, text, **kwargs):
            super().__init__(text, **kwargs)
            self.border_title = title
            self.styles.border = ('round', role_colors[title])
            self.styles.padding = (0, 1)
            self.styles.margin = (0, 0)

    # chat history widget
    class ChatHistory(VerticalScroll):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.styles.scrollbar_size_vertical = 0

        def compose(self):
            yield ChatMessage('system', chat.system)

    class BarePrompt(Input):
        def __init__(self, height, **kwargs):
            super().__init__(**kwargs)
            self.styles.border = ('none', None)
            self.styles.padding = (0, 1)
            self.styles.height = height

    class ChatInput(Static):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.border_title = 'user'
            self.styles.border = ('round', 'white')

        def compose(self):
            yield BarePrompt(id='prompt', height=3, placeholder='Type a message...')

    # textualize chat app
    class ChatApp(App):
        CSS = """
        #prompt {
            background: $surface;
        }
        """

        def compose(self):
            yield Header(id='header')
            yield ChatHistory(id='history')
            yield ChatInput(id='input')

        def on_mount(self):
            prompt = self.query_one('#prompt')
            self.title = f'oneping: {provider}'
            self.set_focus(prompt)

        def on_key(self, event):
            history = self.query_one('#history')
            if event.key == 'PageUp':
                history.scroll_up(animate=False)
            elif event.key == 'PageDown':
                history.scroll_down(animate=False)

        @on(Input.Submitted)
        async def on_input(self, event):
            prompt = self.query_one('#prompt')
            history = self.query_one('#history')

            # ignore empty messages
            if len(message := prompt.value) == 0:
                return
            prompt.clear()

            # mount user query and start response
            response = ChatMessage('assistant', '...')
            await history.mount(ChatMessage('user', message))
            await history.mount(response)

            # make update method
            def update(reply):
                response.update(reply)
                history.scroll_end()

            # send message
            stream = chat.stream(message)
            self.pipe_stream(stream, update)

        @work(thread=True)
        async def pipe_stream(self, stream, setter):
            async for reply in cumcat(stream):
                self.call_from_thread(setter, reply)

    # run app
    app = ChatApp()
    app.run()

# main interface
if __name__ == '__main__':
    import sys
    provider = sys.argv[1] if len(sys.argv) > 1 else 'local'
    main(provider)
