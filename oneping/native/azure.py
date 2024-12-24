# azure interfaces

from openai import AzureOpenAI, AsyncAzureOpenAI

from ..providers import (
    DEFAULT_SYSTEM, OPENAI_MODEL, OPENAI_WHISPER, AZURE_API_VERSION, AZURE_KEYENV,
    payload_openai, response_openai_native, stream_openai_native, transcribe_openai
)

from .utils import client_oneshot

class Client:
    def __init__(self, endpoint, api_key=None, api_version=AZURE_API_VERSION):
        api_key = api_key if api_key is not None else os.environ.get(AZURE_KEYENV)
        self.client = AzureOpenAI(
            api_key=api_key, api_version=api_version, azure_endpoint=endpoint
        )

    def reply(self, query, history=None, system=DEFAULT_SYSTEM, model=OPENAI_MODEL, **kwargs):
        payload = payload_openai(query, system=system, history=history)
        response = self.client.chat.completions.create(model=model, **payload, **kwargs)
        return response_openai_native(response)

    async def reply_async(self, query, history=None, system=DEFAULT_SYSTEM, model=OPENAI_MODEL, **kwargs):
        payload = payload_openai(query, system=system, history=history)
        response = await self.client.chat.completions.create(model=model, **payload, **kwargs)
        return response_openai_native(response)

    def stream(self, query, history=None, system=DEFAULT_SYSTEM, model=OPENAI_MODEL, **kwargs):
        payload = payload_openai(query, system=system, history=history)
        response = self.client.chat.completions.create(model=model, stream=True, **payload, **kwargs)
        for chunk in response:
            yield stream_openai_native(chunk)

    async def stream_async(self, query, history=None, system=DEFAULT_SYSTEM, model=OPENAI_MODEL, **kwargs):
        payload = payload_openai(query, system=system, history=history)
        response = await self.client.chat.completions.create(model=model, stream=True, **payload, **kwargs)
        async for chunk in response:
            yield stream_openai_native(chunk)

    def transcribe(self, audio, model=OPENAI_WHISPER, **kwargs):
        response = self.client.audio.transcriptions.create(model=model, file=audio)
        return transcribe_openai(response)

# standalone functions
azure_oneshot = lambda f: client_oneshot(f, Client, ['endpoint', 'api_key', 'api_version'])
reply = azure_oneshot('reply')
reply_async = azure_oneshot('reply_async')
stream = azure_oneshot('stream')
stream_async = azure_oneshot('stream_async')
transcribe = azure_oneshot('transcribe')
