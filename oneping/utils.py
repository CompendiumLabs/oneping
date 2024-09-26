# general utils

import asyncio

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
