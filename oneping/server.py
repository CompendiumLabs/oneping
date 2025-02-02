# llm servers

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

# this accepts model = provider/model like openrouter
def patch_model(data):
    if 'provider' not in data and 'model' in data:
        if '/' in (model := data.pop('model')):
            provider, model = model.split('/', maxsplit=1)
            return {**data, 'provider': provider, 'model': model}
        else:
            return {**data, 'provider': model}
    raise ValueError(f'Invalid provider/model specified')

def start_router(host='127.0.0.1', port=5000, allow_origins=DEFAULT_ALLOW_ORIGINS, **kwargs):
    import uvicorn
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import PlainTextResponse, StreamingResponse
    from pydantic import BaseModel

    class GenerateRequest(BaseModel):
        query: str
        stream: bool | None = False
        native: bool | None = None
        provider: str | None = None
        model: str | None = None
        system: str | None = None
        prefill: str | None = None
        prediction: str | None = None
        max_tokens: int | None = None
        history: list[dict[str, str]] | None = None

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
        patch = patch_model(data)
        if genreq.stream:
            resp = stream_api(**kwargs, **patch)
            return StreamingResponse(resp, media_type='text/plain')
        else:
            resp = reply_api(**kwargs, **patch)
            return PlainTextResponse(resp)

    uvicorn.run(app, host=host, port=port)
