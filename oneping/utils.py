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
