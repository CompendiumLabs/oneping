# textual chat interface

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

from ..utils import cumcat
from ..chat import Chat

##
## globals
##

# colors
role_colors = {
    'system': '#4caf50',
    'user': '#1e88e5',
    'assistant': '#ff0d57',
}

##
## widgets
##

class ChatMessage(Markdown):
    DEFAULT_CSS = """
    ChatMessage {
        padding: 0 1;
        margin: 0 0;
    }
    """

    def __init__(self, title, text, **kwargs):
        super().__init__(text, **kwargs)
        self.border_title = title
        self.styles.border = ('round', role_colors[title])
        self._text = text

    def on_click(self, event):
        import pyperclip
        pyperclip.copy(self._text)

    def update(self, text):
        self._text = text
        return super().update(text)

# chat history widget
class ChatHistory(VerticalScroll):
    DEFAULT_CSS = """
    ChatHistory {
        scrollbar-size-vertical: 0;
    }
    """

    def __init__(self, system=None, **kwargs):
        super().__init__(**kwargs)
        self.system = system

    def compose(self):
        if self.system is not None:
            yield ChatMessage('system', self.system)

class BareQuery(Input):
    DEFAULT_CSS = """
    BareQuery {
        background: $surface;
        padding: 0 1;
    }
    """

    def __init__(self, height, **kwargs):
        super().__init__(**kwargs)
        self.styles.border = ('none', None)
        self.styles.height = height

class ChatInput(Static):
    DEFAULT_CSS = """
    ChatInput {
        border: round white;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.border_title = 'user'

    def compose(self):
        yield BareQuery(height=3, placeholder='Type a message...')

# textualize chat app
class ChatWindow(Static):
    def __init__(self, stream, system=None, **kwargs):
        super().__init__(**kwargs)
        self.stream = stream
        self.system = system

    def compose(self):
        yield ChatHistory(system=self.system)
        yield ChatInput()

    def on_key(self, event):
        history = self.query_one('ChatHistory')
        if event.key == 'PageUp':
            history.scroll_up(animate=False)
        elif event.key == 'PageDown':
            history.scroll_down(animate=False)

    @on(Input.Submitted)
    async def on_input(self, event):
        query = self.query_one('BareQuery')
        history = self.query_one('ChatHistory')

        # ignore empty messages
        if len(message := query.value) == 0:
            return
        query.clear()

        # mount user query and start response
        response = ChatMessage('assistant', '...')
        await history.mount(ChatMessage('user', message))
        await history.mount(response)

        # make update method
        def update(reply):
            response.update(reply)
            history.scroll_end()

        # send message
        generate = self.stream(message)
        self.pipe_stream(generate, update)

    @work(thread=True)
    async def pipe_stream(self, generate, setter):
        async for reply in cumcat(generate):
            self.app.call_from_thread(setter, reply)

class TextualChat(App):
    def __init__(self, chat, **kwargs):
        super().__init__(**kwargs)
        self.chat = chat
        self.title = f'oneping: {self.chat.provider}'

    def compose(self):
        yield Header(id='header')
        yield ChatWindow(self.chat.stream_async, system=self.chat.system)

    def on_mount(self):
        query = self.query_one('BareQuery')
        self.set_focus(query)

# textual powered chat interface
def main(**kwargs):
    chat = Chat(**kwargs)
    app = TextualChat(chat)
    app.run()
