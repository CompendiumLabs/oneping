# textual chat interface

import re
import os

from textual import on, work
from textual.app import App, ComposeResult
from textual.widget import Widget
from textual.widgets import Header, Input, Static, Markdown, Label
from textual.containers import Vertical, VerticalScroll
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
    'system': '#52a18b',
    'user': '#1e88e5',
    'assistant': '#d576f6',
}

##
## sidebar
##

class Sidebar(Widget):
    DEFAULT_CSS = """
    Sidebar {
        width: 30;
        layer: sidebar;
        dock: left;
        offset-x: -100%;

        border-right: #cccccc;

        transition: offset 100ms;

        &.-visible {
            offset-x: 0;
        }

        & > Vertical {
            margin: 1 2;
        }
    }

    #history_title {
        width: 100%;
        text-align: center;
        border: round #d576f6;
    }

    Sidebar > Vertical > Label {
        margin-bottom: 1;
        text-wrap: wrap;
    }
    """

    def __init__(self, convo, **kwargs):
        super().__init__(**kwargs)
        self.convo = convo

    def compose(self):
        with Vertical():
            yield Label("Chat History", id='history_title')
            for title in self.convo:
                yield Label(title)


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
        background: transparent;
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

class ConvoStore:
    def __init__(self, store):
        self.store = store
        self.load_store()

    @staticmethod
    def parse_convo(markdown):
        # match title (#!)
        title_match = re.match(r'^#! (.*)\n', markdown)
        if title_match is None: return None
        title = title_match.group(1)

        # match messages
        chunks = re.split(r'\n\n(SYSTEM|USER|ASSISTANT): ', markdown)
        if len(chunks) == 1 or len(chunks) % 2 == 0: return None

        # message list format
        messages = [
            {'role': role, 'text': text}
            for role, text in zip(chunks[1::2], chunks[2::2])
        ]

        # return title and messages
        return title, messages

    def load_store(self):
        # check for exitence
        self.convo = {}
        if not os.path.exists(self.store):
            return

        # load all convos
        for file in os.listdir(self.store):
            with open(os.path.join(self.store, file), 'r') as fid:
                # parse conversation
                markdown = fid.read().strip()
                result = self.parse_convo(markdown)
                if result is None: continue

                # add to conversation list
                title, messages = result
                self.convo[title] = messages

class TextualChat(App):
    BINDINGS = [("ctrl+s", "toggle_sidebar", "Toggle Sidebar")]

    show_sidebar = reactive(False)

    def __init__(self, chat, store=None, **kwargs):
        super().__init__(**kwargs)
        self.chat = chat

        # load conversation history
        self.store = ConvoStore(store) if store is not None else None

        # set window title
        provider = self.chat.kwargs.get('provider', 'local')
        self.title = f'oneping: {provider}'

    def compose(self):
        yield Header(id='header')
        yield Sidebar(convo=self.store.convo)
        yield ChatWindow(self.chat.stream_async, system=self.chat.system)

    def on_mount(self):
        query = self.query_one('BareQuery')
        self.set_focus(query)

    def action_toggle_sidebar(self):
        if self.store is not None:
            self.show_sidebar = not self.show_sidebar

    def watch_show_sidebar(self, show_sidebar):
        self.query_one(Sidebar).set_class(show_sidebar, "-visible")

# textual powered chat interface
def main(store=None, **kwargs):
    chat = Chat(**kwargs)
    app = TextualChat(chat, store=store)
    app.run()
