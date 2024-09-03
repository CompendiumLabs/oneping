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

def payload_openai(system, prompt):
    return {
        'messages': [
            {'role': 'system', 'content': system},
            {'role': 'user'  , 'content': prompt},
        ],
    }

def payload_anthropic(system, prompt):
    return {
        'system': system,
        'messages': [
            {'role': 'user', 'content': prompt},
        ],
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
