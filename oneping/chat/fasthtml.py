import os
import asyncstdlib as a

from fasthtml.components import Use
from fasthtml.common import (
    serve, FastHTML, Script, Style, Title, Body, Div, Span, Hidden,
    Form, Button, Input, Textarea, Svg
)

from ..default import sprint

##
## global
##

ctrl_enter = 'keydown[ctrlKey&&key==\'Enter\'] from:body'

##
## fasthtml components
##

def ChatInput(placeholder='Type a message...'):
    return Textarea(
        name='prompt', id='prompt', cls='h-[50px] grow rounded bg-gray-100 resize-none outline-none',
        placeholder=placeholder, type='text', hx_swap_oob='true'
    )

def ChatSystem(prompt):
    return Div(prompt, cls='italic text-gray-500')

def ChatBox(role, content, prompt=False):
    extra = 'focus-within:border-blue-400 hover:border-blue-400' if prompt else ''
    boxid = 'prompt-box' if prompt else None
    title = Div(Span(role, cls='relative top-[-5px]'), cls='absolute top-[-10px] left-[10px] h-[20px] font-bold pl-1 pr-1 border border-gray-400 rounded bg-white small-caps cursor-default select-none')
    return Div(id=boxid, cls=f'chat-box relative border border-gray-400 rounded m-2 p-2 pt-3 bg-gray-100 {extra}')(title, content)

def ChatMessage(id=None, message=''):
    hidden = Div(id=id, cls='message-data hidden')(message)
    display = Div(cls='message-display')
    return Div(cls='message')(hidden, display)

def ChatPrompt(route, trigger=ctrl_enter):
    prompt = ChatInput()
    form = Form(
        id='form', cls='flex flex-col grow', hx_ext='ws', ws_send=True,
        ws_connect=route, hx_trigger=trigger
    )(prompt)
    return Div(cls='flex flex-row')(form)

def ChatHistory(history):
    items = (
        (item['role'], item['content']) for item in history
    )
    return [
        ChatBox(role, ChatMessage(f'message-{i}-{role}', message=msg))
        for i, (role, msg) in enumerate(items)
    ]

def ChatList(*children):
    return Div(id='chat', cls='flex flex-col')(*children)

def ChatWindow(system=None, history=None, route='/generate'):
    if history is None:
        history = []
    system = [ChatBox('system', ChatSystem(system))] if system is not None else []
    prompt = ChatBox('user', ChatPrompt(route), prompt=True)
    messages = ChatList(*ChatHistory(history))
    return Div(id='oneping', cls='flex flex-col h-full w-full pt-3 overflow-y-scroll')(*system, messages, prompt)

##
## websocket generator
##

def randhex():
    return os.urandom(4).hex()

async def websocket(prompt, stream, send):
    await send('START')

    # clear prompt input
    await send(ChatInput())

    # create user message
    box_user = ChatBox('user', ChatMessage(message=prompt))
    await send(Div(box_user, hx_swap_oob='beforeend', id='chat'))

    # start assistant message
    msg_asst = f'message-{randhex()}'
    box_asst = ChatBox('assistant', ChatMessage(id=msg_asst, message='...'))
    await send(Div(box_asst, hx_swap_oob='beforeend', id='chat'))

    # stream in assistant response
    async for i, chunk in a.enumerate(stream):
        sprint(chunk)
        swap_op = 'innerHTML' if i == 0 else 'beforeend'
        await send(Span(chunk, hx_swap_oob=swap_op, id=msg_asst))

    await send('DONE')

##
## chat javascript
##

chat_js = """
function focusPrompt() {
    const prompt = document.querySelector('#prompt');
    prompt.focus();
}
function renderBox(box) {
    const data = box.querySelector('.message-data').textContent;
    const display = box.querySelector('.message-display');
    display.innerHTML = marked.parse(data);
}
document.addEventListener('htmx:wsBeforeMessage', event => {
    const message = event.detail.message;
    const prompt_box = document.querySelector('#prompt-box');
    if (message == 'START') {
        prompt_box.classList.add('hidden');
    } else if (message == 'DONE') {
        prompt_box.classList.remove('hidden');
    }
});
document.addEventListener('htmx:wsAfterMessage', event => {
    const last = document.querySelector('#chat > .chat-box:last-child > .message');
    if (last == null) return;
    renderBox(last);
    const chat = document.querySelector('#chat');
    chat.scrollTop = chat.scrollHeight;
});
document.addEventListener('DOMContentLoaded', () => {
    const boxes = document.querySelectorAll('#chat > .chat-box > .message');
    for (const box of boxes) {
        renderBox(box);
    }
    focusPrompt();
});
"""

chat_css = """
.hidden {
    display: none;
}
.message-display ol {
    list-style-type: decimal;
    padding-left: 40px;
}

.message-display ul {
    list-style-type: disc;
    padding-left: 40px;
}

.message-display pre {
    background-color: white;
    border: 1px solid #ddd;
    line-height: 1.2;
    padding: 10px;
}

.message-display code {
    font-family: monospace;
    font-size: 12px;
    white-space: pre-wrap;
}

.message-display *:not(:last-child) {
    margin-bottom: 10px;
}
"""

##
## fasthtml app
##

def FastHTMLChat(chat):
    # create app object
    hdrs = [
        Script(src="https://cdn.tailwindcss.com"),
        Script(src='https://cdn.jsdelivr.net/npm/marked/marked.min.js')
    ]
    app = FastHTML(hdrs=hdrs, ws_hdr=True)

    # connect main
    @app.route('/')
    def index():
        style = Style(chat_css)
        script = Script(chat_js)
        title = Title('Oneping Chat')
        system, history = chat.system, chat.history
        wind = ChatWindow(system=system, history=history)
        body = Body(cls='h-full w-full')(wind)
        return (title, style, script), body

    # connect websocket
    @app.ws('/generate')
    async def generate(prompt: str, send):
        print(f'GENERATE: {prompt}')
        stream = chat.stream_async(prompt)
        await websocket(prompt, stream, send)
        print('\nDONE')

    # return app
    return app
