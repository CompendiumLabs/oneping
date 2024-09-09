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

def payload_openai(prompt, system=None, prefill=None, history=None):
    if type(history) is list:
        messages = history
    elif system is not None:
        messages = [{'role': 'system', 'content': system}]
    else:
        messages = []
    messages.append({'role': 'user', 'content': prompt})
    if prefill is not None:
        messages.append({'role': 'assistant', 'content': prefill})
    return {
        'messages': messages,
    }

def payload_anthropic(prompt, system=None, prefill=None, history=None):
    if type(history) is list:
        messages = history
    else:
        messages = []
    messages.append({'role': 'user', 'content': prompt})
    if prefill is not None:
        messages.append({'role': 'assistant', 'content': prefill})
    payload = {'messages': messages}
    if system is not None:
        payload['system'] = system
    return payload

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
    return chunk['choices'][0]['delta'].get('content', '')

def stream_anthropic(chunk):
    if chunk['type'] == 'content_block_delta':
        return chunk['delta']['text']
    else:
        return ''