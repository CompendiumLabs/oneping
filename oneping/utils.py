# general utils

import asyncio

##
## streaming
##

def sprint(text):
    print(text, end='', flush=True)

def streamer(stream, tee=False):
    text = ''
    for chunk in stream:
        text += chunk
        sprint(chunk)
    if tee:
        return text

async def streamer_async(stream):
    async for chunk in stream:
        sprint(chunk)

async def cumcat(stream):
    reply = ''
    async for chunk in stream:
        reply += chunk
        yield reply
