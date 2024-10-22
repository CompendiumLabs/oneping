# fasthtml chat interface

import os
import asyncstdlib as a

from fasthtml.components import Use
from fasthtml.common import (
    serve, FastHTML, Script, Style, Title, Body, Div, Span, Hidden,
    Form, Button, Input, Textarea, Svg, ScriptX, StyleX
)

from ..utils import sprint
from ..chat import Chat

##
## global
##

scoped_enter = 'keydown[key==\'Enter\'] from:#oneping'

##
## fasthtml components
##

def ChatInput(placeholder='Type a message...'):
    return Textarea(
        name='query', id='query', cls='h-[50px] grow rounded bg-gray-100 resize-none outline-none',
        placeholder=placeholder, type='text', hx_swap_oob='true'
    )

def ChatSystem(prompt):
    return Div(prompt, cls='italic text-gray-500')

def ChatBox(role, content, query=False):
    extra = 'focus-within:border-blue-400 hover:border-blue-400' if query else ''
    boxid = 'query-box' if query else None
    title = Div(Span(role, cls='relative top-[-5px]'), cls='absolute top-[-10px] left-[10px] h-[20px] font-bold pl-1 pr-1 border border-gray-400 rounded bg-white small-caps cursor-default select-none')
    return Div(id=boxid, cls=f'chat-box relative border border-gray-400 rounded m-2 p-2 pt-3 bg-gray-100 {extra}')(title, content)

def ChatMessage(id=None, message=''):
    hidden = Div(id=id, cls='message-data hidden')(message)
    display = Div(cls='message-display')
    return Div(cls='message')(hidden, display)

def ChatPrompt(route, trigger=None, hx_vals=None):
    query = ChatInput()
    form = Form(
        id='query-form', cls='flex flex-col grow', hx_ext='ws', ws_send=True,
        ws_connect=route, hx_trigger=trigger, hx_vals=hx_vals
    )(query)
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

def ChatWindow(system=None, history=None, route='/generate', trigger=scoped_enter, hx_vals=None):
    if history is None:
        history = []
    system = [ChatBox('system', ChatSystem(system))] if system is not None else []
    query = ChatPrompt(route, trigger=trigger, hx_vals=hx_vals)
    query_box = ChatBox('user', query, query=True)
    messages = ChatList(*ChatHistory(history))
    return Div(id='oneping', cls='flex flex-col w-full pt-3')(*system, messages, query_box)

##
## websocket generator
##

def randhex():
    return os.urandom(4).hex()

async def websocket(query, stream, send):
    await send('ONEPING_START')

    # clear query input
    await send(ChatInput())

    # create user message
    box_user = ChatBox('user', ChatMessage(message=query))
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

    await send('ONEPING_DONE')

##
## web content
##

def get_lib_dir():
    return os.path.dirname(__file__)

def ChatCSS():
    css_path = os.path.join(get_lib_dir(), 'web/fasthtml.css')
    return StyleX(css_path)

def ChatJS():
    js_path = os.path.join(get_lib_dir(), 'web/fasthtml.js')
    return ScriptX(js_path)

##
## fasthtml app
##

def FastHTMLChat(chat):
    # create app object
    hdrs = [
        Script(src="https://cdn.tailwindcss.com"),
        Script(src='https://cdn.jsdelivr.net/npm/marked/marked.min.js')
    ]
    app = FastHTML(hdrs=hdrs, exts='ws')

    # connect main
    @app.route('/')
    def index():
        style = ChatCSS()
        script = ChatJS()
        title = Title('Oneping Chat')
        wind = ChatWindow(system=chat.system, history=chat.history)
        body = Body(cls='h-screen w-screen')(wind)
        return (title, style, script), body

    # connect websocket
    @app.ws('/generate')
    async def generate(query: str, send):
        print(f'GENERATE: {query}')
        stream = chat.stream_async(query)
        await websocket(query, stream, send)
        print('\nDONE')

    # return app
    return app

# fasthtml powered chat interface
def main(chat_host='127.0.0.1', chat_port=5000, reload=False, **kwargs):
    import uvicorn
    from fasthtml.common import serve

    # make application
    chat = Chat(**kwargs)
    app = FastHTMLChat(chat)

    # run server
    config = uvicorn.Config(app, host=chat_host, port=chat_port, reload=reload)
    server = uvicorn.Server(config)
    server.run()
