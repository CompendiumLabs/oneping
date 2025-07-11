# textual chat interface

import re
import os
import datetime

from textual import work, Logger
from textual.app import App
from textual.widget import Widget
from textual.widgets import Header, Static, Markdown, Label, TextArea
from textual.containers import Vertical, VerticalScroll
from textual.reactive import reactive
from textual.message import Message

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
    def __init__(self, convo, **kwargs):
        super().__init__(**kwargs)
        self.convo = convo

    def compose(self):
        with Vertical():
            yield Label("Chat History", id='history_title')
            for convo in self.convo.values():
                if convo is None: continue
                yield Label(convo['title'])

##
## widgets
##

def make_text(text, gen=False):
    return f'{text} {" ..." if gen else ""}'

class ChatMessage(Markdown):
    generating = reactive(False)

    def __init__(self, title, text, gen=False, **kwargs):
        text0 = make_text(text, gen)
        super().__init__(text0, **kwargs)
        self.border_title = title
        self.styles.border = ('round', role_colors[title])
        self._text = text
        self.generating = gen

    def on_click(self, event):
        try:
            import pyperclip
            pyperclip.copy(self._text)
        except Exception:
            pass

    def update_text(self, text=None):
        if text is None:
            text = self._text
        else:
            self._text = text
        disp = make_text(text, self.generating)
        return super().update(disp)

    def watch_generating(self, generating):
        self.update_text()

# chat history widget
class ChatHistory(VerticalScroll):
    def __init__(self, system=None, **kwargs):
        super().__init__(**kwargs)
        self.system = system

    def compose(self):
        if self.system is not None:
            yield ChatMessage('system', self.system)

class ChatInput(TextArea):
    class Submitted(Message):
        def __init__(self, text: str) -> None:
            self.text = text
            super().__init__()

    def __init__(self, **kwargs):
        super().__init__(highlight_cursor_line=False, **kwargs)

    def on_key(self, event):
        if event.key == 'ctrl+enter':
            self.insert('\n')
            event.prevent_default()
        elif event.key == 'enter':
            if len(query := self.text.strip()) > 0:
                message = self.Submitted(query)
                self.post_message(message)
                self.clear()
            event.prevent_default()

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
        if event.key == 'pageup':
            history.scroll_up(animate=False)
        elif event.key == 'pagedown':
            history.scroll_down(animate=False)

    async def on_chat_input_submitted(self, message):
        await self.submit_query(message.text)

    async def submit_query(self, query):
        # make new messages
        user = ChatMessage('user', query, gen=False)
        response = ChatMessage('assistant', '', gen=True)

        # mount new messages
        history = self.query_one('ChatHistory')
        await history.mount(user)
        await history.mount(response)

        # make update method
        def update(reply):
            if reply is None:
                self.log.debug('STREAM DONE')
                response.generating = False
                return
            response.update_text(reply)
            history.scroll_end(animate=False)

        # send message
        generate = self.stream(query)
        self.log.debug(f'STARTING STREAM: {query}')
        self.pipe_stream(generate, update)

    @work(thread=True)
    async def pipe_stream(self, generate, setter):
        async for reply in cumcat(generate):
            self.app.call_from_thread(setter, reply)
        self.app.call_from_thread(setter, None)

class ConvoStore:
    def __init__(self, store):
        self.store = store
        self.load_store()

    @staticmethod
    def load_convo(path):
        # read markdown file
        timestamp = datetime.datetime.now()
        with open(path, 'r') as fid:
            markdown = fid.read().strip()

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
        return {
            'title': title,
            'messages': messages,
            'timestamp': timestamp,
        }

    def load_store(self):
        # check for exitence
        self.convo = {}
        if not os.path.exists(self.store):
            return

        # load all convos
        for file in os.listdir(self.store):
            path = os.path.join(self.store, file)
            self.convo[file] = self.load_convo(path)

class TextualChat(App):
    CSS = """
    ChatMessage {
        background: transparent;
        padding: 0 1;
        margin: 0 0;
    }

    ChatHistory {
        scrollbar-size-vertical: 0;
    }

    ChatInput {
        background: transparent;
        border: round white;
        padding: 0 1;
        height: 6;
    }

    ChatInput > TextArea {
        height: 100%;
    }

    ChatWindow {
        background: transparent;
    }

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
        if self.store is not None:
            yield Sidebar(convo=self.store.convo)
        yield ChatWindow(self.chat.stream_async, system=self.chat.system)

    def on_mount(self):
        query = self.query_one('ChatInput')
        history = self.query_one('ChatHistory')
        self.set_focus(query)
        history.scroll_end(animate=False)

    def on_key(self, event):
        if event.key == 'ctrl+s':
            if self.store is not None:
                self.show_sidebar = not self.show_sidebar
            event.prevent_default()
        elif event.key == 'ctrl+c':
            self.exit()
            event.prevent_default()

    def watch_show_sidebar(self, show_sidebar):
        if self.store is not None:
            sidebar = self.query_one(Sidebar)
            sidebar.set_class(show_sidebar, "-visible")

# textual powered chat interface
def main(store=None, **kwargs):
    chat = Chat(**kwargs)
    app = TextualChat(chat, store=store)
    app.run()
