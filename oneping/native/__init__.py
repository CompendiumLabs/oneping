# native library interfaces

##
## dummy function
##

class DummyFunction:
    def __init__(self, package):
        self.package = package

    def __call__(self, *args, **kwargs):
        raise Exception(f'Please install package: {self.package}')

##
## anthropic
##

try:
    from .anthropic import (
        get_llm_response as get_anthropic_response,
        stream_llm_response as stream_anthropic_response,
        async_llm_response as async_anthropic_response,
    )
except ImportError:
    dummy_anthropic = DummyFunction('anthropic')
    get_anthropic_response = dummy_anthropic
    stream_anthropic_response = dummy_anthropic

##
## openai
##

try:
    from .openai import (
        get_llm_response as get_openai_response,
        stream_llm_response as stream_openai_response,
        async_llm_response as async_openai_response,
    )
except ImportError:
    dummy_openai = DummyFunction('openai')
    get_openai_response = dummy_openai
    stream_openai_response = dummy_openai

##
## fireworks
##

try:
    from .fireworks import (
        get_llm_response as get_fireworks_response,
        stream_llm_response as stream_fireworks_response,
        async_llm_response as async_fireworks_response,
    )
except ImportError:
    dummy_fireworks = DummyFunction('fireworks-ai')
    get_fireworks_response = dummy_fireworks
    stream_fireworks_response = dummy_fireworks
