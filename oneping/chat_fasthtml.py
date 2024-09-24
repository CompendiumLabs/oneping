from fasthtml.components import Use
from fasthtml.common import serve, FastHTML, Script, Title, Body, Div, Span, Hidden, Form, Button, Input, Textarea, Svg

##
## global
##

ctrl_enter = 'keydown[ctrlKey&&key==\'Enter\'] from:body'

def sprint(text):
    print(text, end='', flush=True)

##
## fasthtml components
##

def ChatInput(placeholder='Enter a query...'):
    return Textarea(
        name='prompt', id='prompt', cls='h-[50px] grow rounded bg-gray-100 resize-none outline-none',
        placeholder=placeholder, type='text', hx_swap_oob='true'
    )

def ChatSystem(prompt):
    return Div(prompt, cls='italic text-gray-500')

def ChatBox(role, content, id=None):
    title = Div(Span(role, cls='relative top-[-5px]'), cls='absolute top-[-10px] left-[10px] h-[20px] font-bold pl-1 pr-1 border border-gray-400 rounded bg-white small-caps')
    return Div(id=id, cls='chat-box relative border border-gray-400 rounded m-2 p-2 pt-3 bg-gray-100')(title, content)

def ChatMessage(id, message=''):
    return Div(id=id, cls='whitespace-pre-wrap')(message)

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
    prompt = ChatBox('user', ChatPrompt(route))
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
    hdrs = [Script(src="https://cdn.tailwindcss.com")]
    app = FastHTML(hdrs=hdrs, ws_hdr=True)

    # connect main
    @app.route('/')
    def index():
        title = Title('Oneping Chat')
        wind = ChatWindow(chat, '/generate')
        body = Body(cls='bg-gray-100 h-full w-full')(wind)
        return title, body

    # connect websocket
    @app.ws('/generate')
    async def generate(prompt: str, send):
        print(f'GENERATE: {prompt}')
        await websocket(prompt, chat, send)
        print('\nDONE')

    # return app
    return app
