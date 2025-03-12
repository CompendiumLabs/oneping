# llm servers

import json
import subprocess
from itertools import chain

from .api import reply as reply_api, stream as stream_api

DEFAULT_ALLOW_ORIGINS = [
    'http://localhost',
    'http://127.0.0.1',
]

def start_llama_cpp(model, n_gpu_layers=-1, **kwargs):
    args = chain(*[(f'--{k}', str(v)) for k, v in kwargs.items()])
    opts = ['--model', model, '--n_gpu_layers', n_gpu_layers, *args]
    cmds = ['python', '-m', 'llama_cpp.server', *opts]
    subprocess.run([str(x) for x in cmds])

# map messages back into history for rebroadcasting
# this accepts model = provider/model like openrouter
def patch_payload(data):
    if 'provider' not in data and 'model' in data:
        if '/' in (model := data.pop('model')):
            data['provider'], data['model'] = model.split('/', maxsplit=1)
        else:
            data['provider'] = model
    return data

def generate_sse(stream):
    for chunk in stream:
        data = json.dumps(chunk)
        yield f'data: {data}\n\n'
    yield 'data: [DONE]\n\n'

def start_router(host='127.0.0.1', port=5000, allow_origins=DEFAULT_ALLOW_ORIGINS, **kwargs):
    import uvicorn
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import PlainTextResponse, StreamingResponse
    from pydantic import BaseModel

    MessageDict = dict[str, str]
    class GenerateRequest(BaseModel):
        query: str | MessageDict | list[MessageDict]
        stream: bool | None = False
        native: bool | None = None
        provider: str | None = None
        model: str | None = None
        system: str | None = None
        prefill: str | None = None
        prediction: MessageDict | None = None
        max_tokens: int | None = None
        history: list[MessageDict] | None = None

    app = FastAPI()

    if allow_origins is not None:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=allow_origins,
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
        )

    @app.post('/chat')
    async def chat(genreq: GenerateRequest):
        data = genreq.model_dump(exclude_none=True)
        patch = patch_payload(data)
        if patch.get('stream', False):
            stream = stream_api(**kwargs, **patch)
            sse = generate_sse(stream)
            return StreamingResponse(sse, media_type='text/event-stream')
        else:
            reply = reply_api(**kwargs, **patch)
            return PlainTextResponse(reply)

    uvicorn.run(app, host=host, port=port)
