# xai interface

import xai_sdk

from ..default import SYSTEM, OPENAI_MODEL, payload_openai, response_openai, stream_openai

async def get_llm_response(prompt, api_key=None, model=OPENAI_MODEL, system=SYSTEM, **kwargs):
    client = xai_sdk.Client(api_key=api_key)
    conversation = client.chat.create_conversation()
    response = await conversation.add_response_no_stream(prompt)
    return response.message

async def stream_llm_response(prompt, api_key=None, model=OPENAI_MODEL, system=SYSTEM, **kwargs):
    client = xai_sdk.Client(api_key=api_key)
    conversation = client.chat.create_conversation()
    response, _ = conversation.add_response(prompt)
    for token in response:
        yield token
