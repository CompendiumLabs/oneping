# prompt llm interface

from ..chat import Chat
from ..utils import sprint

from prompt_toolkit import prompt, print_formatted_text, HTML

def make_header(name, color='green'):
    return HTML(f'<{color}>{name}></{color}> ')

def loop(provider='local', name=None, **kwargs):
    # get name
    if name is None:
        name = provider

    # initialize chat
    chat = Chat(provider=provider, **kwargs)

    # main prompt loop
    while True:
        # get query
        query = prompt(make_header('user', 'ansigreen'))

        # skip if empty
        if query.strip() == '':
            continue

        # stream reply
        print()
        print_formatted_text(make_header(name, 'ansired'), end='')
        for s in chat.stream(query):
            sprint(s)
        print('\n')

def main(**kwargs):
    # exit gracefully
    try:
        loop(**kwargs)
    except (KeyboardInterrupt, EOFError):
        print()
        pass
