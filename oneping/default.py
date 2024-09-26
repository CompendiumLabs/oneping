# default arguments

import asyncio

##
## models
##

ANTHROPIC_MODEL = 'claude-3-5-sonnet-20240620'
OPENAI_MODEL = 'gpt-4o'
FIREWORKS_MODEL = 'accounts/fireworks/models/llama-v3-70b-instruct'

##
## system prompt
##

SYSTEM = 'You are a helpful and knowledgeable AI assistant. Answer the queries provided to the best of your ability.'

##
## message payloads
##

def payload_openai(prompt=None, system=None, prefill=None, history=None):
    if system is not None:
        messages = [{'role': 'system', 'content': system}]
    else:
        messages = []
    if type(history) is list:
        messages += history
    if prompt is not None:
        messages.append({'role': 'user', 'content': prompt})
    if prefill is not None:
        messages.append({'role': 'assistant', 'content': prefill})
    return {
        'messages': messages,
    }

def payload_anthropic(prompt=None, system=None, prefill=None, history=None):
    if type(history) is list:
        messages = [*history]
    else:
        messages = []
    if prompt is not None:
        messages.append({'role': 'user', 'content': prompt})
    if prefill is not None:
        messages.append({'role': 'assistant', 'content': prefill})
    payload = {'messages': messages}
    if system is not None:
        payload['system'] = system
    return payload

##
## response extraction
##

def response_openai(reply):
    choice = reply['choices'][0]
    return choice['message']['content']

def response_anthropic(reply):
    content = reply['content'][0]
    return content['text']

def stream_openai(chunk):
    return chunk['choices'][0]['delta'].get('content', '')

def stream_anthropic(chunk):
    if chunk['type'] == 'content_block_delta':
        return chunk['delta']['text']
    else:
        return ''

def response_anthropic_native(reply):
    return reply.content[0].text

def stream_anthropic_native(chunk):
    if chunk.type == 'content_block_delta':
        return chunk.delta.text
    else:
        return ''

def response_openai_native(reply):
    return reply.choices[0].message.content

def stream_openai_native(chunk):
    text = chunk.choices[0].delta.content
    if text is not None:
        return text
    else:
        return ''

##
## streaming
##

def sprint(text):
    print(text, end='', flush=True)

def streamer(stream):
    for chunk in stream:
        sprint(chunk)

async def streamer_async(stream):
    async for chunk in stream:
        sprint(chunk)

async def cumcat(stream):
    reply = ''
    async for chunk in stream:
        reply += chunk
        yield reply

def syncify(async_gen):
    # get or create event loop
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # run until stopped
    try:
        while True:
            yield loop.run_until_complete(async_gen.__anext__())
    except StopAsyncIteration:
        pass
