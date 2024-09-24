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
## utils
##

# stream printer
def sprint(s):
    print(s, end='', flush=True)

async def cumcat(stream):
    reply = ''
    async for chunk in stream:
        reply += chunk
        yield reply

##
## widgets
##

class ChatMessage(Markdown):
    def __init__(self, title, text, **kwargs):
        super().__init__(text, **kwargs)
        self.border_title = title
        self.styles.border = ('round', role_colors[title])
        self.styles.padding = (0, 1)
        self.styles.margin = (0, 0)

# chat history widget
class ChatHistory(VerticalScroll):
    def __init__(self, system, **kwargs):
        super().__init__(**kwargs)
        self.styles.scrollbar_size_vertical = 0
        self.system = system

    def compose(self):
        yield ChatMessage('system', self.system)

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
class TextualChat(App):
    CSS = """
    #prompt {
        background: $surface;
    }
    """

    def __init__(self, chat, **kwargs):
        super().__init__(**kwargs)
        self.chat = chat

    def compose(self):
        yield Header(id='header')
        yield ChatHistory(self.chat.system, id='history')
        yield ChatInput(id='input')

    def on_mount(self):
        prompt = self.query_one('#prompt')
        self.title = f'oneping: {self.chat.provider}'
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
        stream = self.chat.stream(message)
        self.pipe_stream(stream, update)

    @work(thread=True)
    async def pipe_stream(self, stream, setter):
        async for reply in cumcat(stream):
            self.call_from_thread(setter, reply)
