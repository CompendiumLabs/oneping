# default arguments

##
## models
##

ANTHROPIC_MODEL = 'claude-3-5-sonnet-20240620'
OPENAI_MODEL = 'gpt-4o'

##
## system prompt
##

SYSTEM = 'You are a helpful and knowledgable AI assistant. Answer the queries provided to the best of your ability.'

##
## message payloads
##

def payload_openai(prompt, system=SYSTEM, prefill=None, history=None):
    if type(history) is list:
        messages = history
    else:
        messages = [{'role': 'system', 'content': system}]
    messages.append({'role': 'user', 'content': prompt})
    if prefill is not None:
        messages.append({'role': 'assistant', 'content': prefill})
    return {
        'messages': messages,
    }

def payload_anthropic(prompt, system=SYSTEM, prefill=None, history=None):
    if type(history) is list:
        messages = history
    else:
        messages = []
    messages.append({'role': 'user', 'content': prompt})
    if prefill is not None:
        messages.append({'role': 'assistant', 'content': prefill})
    return {
        'system': system,
        'messages': messages,
    }

##
## response extraction
##

def response_openai(reply):
    choice = reply['choices'][0]
    return choice['message']['content']

def response_anthropic(reply):
    content = reply['content'][0]
    return content['text']

def stream_openai(chunk):
    return chunk.choices[0].delta.content
