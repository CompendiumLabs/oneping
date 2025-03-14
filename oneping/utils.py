# general utils

import re
import base64
import asyncio
import mimetypes

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

##
## image utils
##

def load_image_uri(image):
    media_type, _ = mimetypes.guess_type(image)
    with open(image, 'rb') as f:
        binary = f.read()
    data = base64.b64encode(binary).decode('utf-8')
    return f'data:{media_type};base64,{data}'

def parse_image_uri(image):
    media_type, data = re.match(r'data:(.*);base64,(.*)', image).groups()
    return media_type, data
