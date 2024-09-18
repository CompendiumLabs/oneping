import sys
import fire

from .curl import get_llm_response
from .server import run_llama_server
from .chat import main

def chat(
    provider='local', system=None, url=None, port=8000, api_key=None, model=None,
    max_tokens=1024, **kwargs
):
    return main(
        provider=provider, system=system, url=url, port=port, api_key=api_key, model=model,
        max_tokens=max_tokens, **kwargs
    )

def reply(
    prompt=None, provider='local', system=None, prefill=None, history=None, url=None,
    port=8000, api_key=None, model=None, max_tokens=1024, stream=False, **kwargs
):
    # read from stdin if no prompt
    if prompt is None:
        prompt = sys.stdin.read()

    # get response
    return get_llm_response(
        prompt, provider=provider, system=system, prefill=prefill, history=history, url=url,
        port=port, api_key=api_key, model=model, max_tokens=max_tokens, stream=stream, **kwargs
    )

def serve(model, n_gpu_layers=-1, **kwargs):
    return run_llama_server(model, n_gpu_layers=n_gpu_layers, **kwargs)

if __name__ == '__main__':
    fire.Fire({
        'chat': chat,
        'reply': reply,
        'serve': serve,
    })
