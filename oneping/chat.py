# chat interface to curl

from .default import SYSTEM
from .curl import get_llm_response, stream_llm_response, compose_history

# stream printer
def sprint(s):
    print(s, end='', flush=True)

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
    from textual.app import App, ComposeResult
    from textual.widget import Widget
    from textual.widgets import Header, Input, Static
    from textual.events import Key
    from textual.reactive import reactive
    from rich.style import Style
    from rich.text import Text
    from rich.panel import Panel

    # make chat history
    chat = Chat(provider, **kwargs)

    class ChatMessage(Static):
        def __init__(self, title, text, **kwargs):
            super().__init__(**kwargs)
            self.title = title
            self.text = text

        def render(self) -> str:
            border_color = role_colors[self.title]
            title_style = Style(bold=True, color=border_color)
            border_style = Style(color=border_color)
            title = Text(self.title, style=title_style)
            return Panel(
                self.text, title=title, title_align='left', border_style=border_style
            )

    # chat history widget
    class ChatHistory(Static):
        history = reactive([], recompose=True)

        def compose(self) -> ComposeResult:
            yield ChatMessage('system', chat.system)
            for message in self.history:
                role, text = message['role'], message['content']
                yield ChatMessage(role, text)

    class ChatInput(Static):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.styles.border = ('round', 'white')
            self.border_title = 'user'

        def compose(self) -> ComposeResult:
            prompt = Input(id='prompt')
            prompt.styles.padding = (0, 1)
            prompt.styles.border = ('none', None)
            prompt.styles.height = 3
            yield prompt

    # textualize chat app
    class ChatApp(App):
        CSS = """
        #prompt {
            background: $surface;
        }
        """

        def compose(self) -> ComposeResult:
            yield Header()
            yield ChatHistory(id='history')
            yield ChatInput(id='input')

        def on_mount(self) -> None:
            self.title = f'oneping: {provider}'

        def on_key(self, event: Key) -> None:
            if event.key == 'enter':
                prompt = self.query_one('#prompt')
                chist = self.query_one('#history')
                if len(message := prompt.value) > 0:
                    reply = ''.join(chat.stream(message))
                    chist.history = chat.history
                    prompt.value = ''

        def send_message(self, message: str) -> None:
            chat(message)

    # run app
    app = ChatApp()
    app.run()

# main interface
if __name__ == '__main__':
    import sys
    provider = sys.argv[1] if len(sys.argv) > 1 else 'local'
    main(provider)
