import sys
import fire

from .curl import get_llm_response, stream_llm_response
from .chat import chat_main
from .server import run_llama_server

def reply(
    prompt=None, provider='local', system=None, prefill=None,  url=None, port=8000,
    api_key=None, model=None, max_tokens=1024, **kwargs
):
    # read from stdin if no prompt
    if prompt is None:
        prompt = sys.stdin.read()

    # get response
    return get_llm_response(
        prompt, provider=provider, system=system, prefill=prefill, url=url,
        port=port, api_key=api_key, model=model, max_tokens=max_tokens, **kwargs
    )

async def stream(
    prompt=None, provider='local', system=None, prefill=None, url=None, port=8000,
    api_key=None, model=None, max_tokens=1024, **kwargs
):
    # read from stdin if no prompt
    if prompt is None:
        prompt = sys.stdin.read()

    # get stream response
    stream = stream_llm_response(
        prompt, provider=provider, system=system, prefill=prefill, url=url,
        port=port, api_key=api_key, model=model, max_tokens=max_tokens, **kwargs
    )

    # print stream
    async for chunk in stream:
        print(chunk, end='', flush=True)
    print()

def chat(
    interface='textual', provider='local', system=None, url=None, port=8000, api_key=None, model=None,
    max_tokens=1024, chat_host='127.0.0.1', chat_port=5000, **kwargs
):
    chat_main(
        interface=interface, provider=provider, system=system, url=url, port=port, api_key=api_key,
        model=model, max_tokens=max_tokens, chat_host=chat_host, chat_port=chat_port, **kwargs
    )

def serve(model, n_gpu_layers=-1, **kwargs):
    return run_llama_server(model, n_gpu_layers=n_gpu_layers, **kwargs)

if __name__ == '__main__':
    fire.Fire({
        'chat': chat,
        'reply': reply,
        'stream': stream,
        'serve': serve,
    })
