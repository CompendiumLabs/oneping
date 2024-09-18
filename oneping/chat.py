# chat interface to curl
# https://textual.textualize.io/blog/2024/09/15/anatomy-of-a-textual-user-interface/

from .default import SYSTEM
from .curl import get_llm_response, stream_llm_response, compose_history

# stream printer
def sprint(s):
    print(s, end='', flush=True)

def cumcat(stream):
    reply = ''
    for chunk in stream:
        reply += chunk
        yield reply

# chat interface
class Chat:
    def __init__(self, provider='local', system=None, **kwargs):
        self.provider = provider
        self.system = SYSTEM if system is None else system
        self.kwargs = kwargs
        self.history = []

    def __call__(self, prompt, **kwargs):
        return self.chat(prompt, **kwargs)

    def chat(self, prompt, prefill=None, **kwargs):
        # get full history and text
        self.history, text = get_llm_response(
            prompt, history=self.history, prefill=prefill, system=self.system, **self.kwargs, **kwargs
        )

        # return text
        return text

    def stream(self, prompt, prefill=None, **kwargs):
        # get input history (plus prefill) and stream
        self.history, replies = stream_llm_response(
            prompt, history=self.history, prefill=prefill, system=self.system, **self.kwargs, **kwargs
        )

        # yield text stream
        reply = ''
        for chunk in replies:
            yield chunk
            reply += chunk

        # update final history
        self.history = compose_history(self.history, reply)

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
    from textual.widgets import Header, Input, Static, Log
    from textual.events import Key
    from textual.reactive import reactive
    from rich.style import Style
    from rich.text import Text
    from rich.panel import Panel

    # make chat history
    chat = Chat(provider, **kwargs)

    class ChatMessage(Static):
        def __init__(self, title, text, **kwargs):
            super().__init__(text, **kwargs)
            self.border_title = title
            self.styles.border = ('round', role_colors[title])
            self.styles.padding = (0, 1)

    # chat history widget
    class ChatHistory(Static):
        def compose(self) -> ComposeResult:
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

        def compose(self) -> ComposeResult:
            yield BarePrompt(id='prompt', height=3)

    # textualize chat app
    class ChatApp(App):
        CSS = """
        #prompt {
            background: $surface;
        }
        """

        def compose(self) -> ComposeResult:
            yield Header(id='header')
            yield ChatHistory(id='history')
            yield ChatInput(id='input')

        def on_mount(self) -> None:
            self.title = f'oneping: {provider}'

        @on(Input.Submitted)
        async def on_input(self, event: Input.Submitted) -> None:
            prompt = self.query_one('#prompt')
            history = self.query_one('#history')

            # ignore empty messages
            if len(message := prompt.value) == 0:
                return
            prompt.value = ''

            # mount user query and start response
            response = ChatMessage('assistant', '')
            history.mount(ChatMessage('user', message))
            history.mount(response)

            # send message
            stream = chat.stream(message)
            self.pipe_stream(stream, response.update)

        @work(thread=True)
        def pipe_stream(self, stream, setter) -> None:
            for reply in cumcat(stream):
                self.call_from_thread(setter, reply)

    # run app
    app = ChatApp()
    app.run()

# main interface
if __name__ == '__main__':
    import sys
    provider = sys.argv[1] if len(sys.argv) > 1 else 'local'
    main(provider)
