import fire

from .curl import get_llm_response
from .server import run_llama_server

if __name__ == '__main__':
    fire.Fire({
        'serve': run_llama_server,
        'chat': get_llm_response,
    })
