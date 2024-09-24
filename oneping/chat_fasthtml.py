from fasthtml.components import Use
from fasthtml.common import (
    serve, FastHTML, Script, Style, Title, Body, Div, Span, Hidden,
    Form, Button, Input, Textarea, Svg
)

##
## global
##

ctrl_enter = 'keydown[ctrlKey&&key==\'Enter\'] from:body'

def sprint(text):
    print(text, end='', flush=True)

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

def ChatMessage(id, message=''):
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

def ChatWindow(chat, route):
    system = ChatBox('system', ChatSystem(chat.system))
    prompt = ChatBox('user', ChatPrompt(route), prompt=True)
    messages = ChatList(*ChatHistory(chat.history))
    return Div(id='oneping', cls='flex flex-col h-full w-full pt-3 overflow-y-scroll')(system, messages, prompt)

##
## websocket generator
##

async def websocket(prompt, chat, send):
    await send('START')

    # clear prompt input
    await send(ChatInput())

    # create user message
    msg_user = f'message-{len(chat.history)}-user'
    box_user = ChatBox('user', ChatMessage(msg_user, message=prompt))
    await send(Div(box_user, hx_swap_oob='beforeend', id='chat'))

    # start assistant message
    msg_asst = f'message-{len(chat.history)+1}-asst'
    box_asst = ChatBox('assistant', ChatMessage(msg_asst))
    await send(Div(box_asst, hx_swap_oob='beforeend', id='chat'))

    # stream in assistant response
    await send(Span('...', hx_swap_oob='beforeend', id=msg_asst))
    swap_op = 'innerHTML'
    async for chunk in chat.stream(prompt):
        sprint(chunk)
        span = Span(chunk, hx_swap_oob=swap_op, id=msg_asst)
        await send(span)
        swap_op = 'beforeend'

    await send('DONE')

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

    # markdown rendering
    script = Script("""
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
    """)

    # markdown style
    style = Style("""
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
    }

    .message-display code {
        font-family: monospace;
        font-size: 12px;
        white-space: pre-wrap;
        margin: 0 !important;
    }

    .message-display *:not(:last-child) {
        margin-bottom: 10px;
    }
    """)

    # connect main
    @app.route('/')
    def index():
        title = Title('Oneping Chat')
        wind = ChatWindow(chat, '/generate')
        body = Body(cls='h-full w-full')(wind)
        return (title, style, script), body

    # connect websocket
    @app.ws('/generate')
    async def generate(prompt: str, send):
        print(f'GENERATE: {prompt}')
        await websocket(prompt, chat, send)
        print('\nDONE')

    # return app
    return app
