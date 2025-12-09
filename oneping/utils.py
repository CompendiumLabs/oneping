# general utils

import re
import base64
import asyncio
import mimetypes

##
## config class
##

class Config(dict):
    def __getitem__(self, key):
        if key in self:
            return super().__getitem__(key)
        else:
            return None

    def __getattr__(self, key):
        return self[key]

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

def make_image_uri(data, media_type='image/png'):
    data = base64.b64encode(data).decode('utf-8')
    return f'data:{media_type};base64,{data}'

def split_image_uri(image):
    match = re.match(r'data:(.*);base64,(.*)', image)
    if match is None:
        raise ValueError(f'Invalid image URI: {image}')
    media_type, base64_data = match.groups()
    return media_type, base64_data

def parse_image_uri(image):
    media_type, base64_data = split_image_uri(image)
    data = base64.b64decode(base64_data)
    return media_type, data

def load_image_uri(image, media_type=None):
    if media_type is None:
        media_type, _ = mimetypes.guess_type(image)
    with open(image, 'rb') as f:
        binary = f.read()
    return make_image_uri(binary, media_type=media_type)

def ensure_image_uri(image, media_type=None):
    if image is None:
        return None
    elif isinstance(image, str):
        if image.startswith('data:'):
            return image
        else:
            return load_image_uri(image, media_type=media_type)
    elif isinstance(image, bytes):
        if media_type is None:
            return make_image_uri(image)
        else:
            return make_image_uri(image, media_type=media_type)
    else:
        raise ValueError(f'Invalid image type: {type(image)}')
