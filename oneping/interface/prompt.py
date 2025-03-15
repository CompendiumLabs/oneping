# prompt llm interface

from ..chat import Chat
from ..utils import sprint

from rich import print as rprint
from prompt_toolkit import prompt

def print_header(name, color='green'):
    rprint(f'[bold {color}]{name}>[/bold {color}] ', end='')

def loop(provider='local', name=None, **kwargs):
    # get name
    if name is None:
        name = provider

    # initialize chat
    chat = Chat(provider=provider, **kwargs)

    # main prompt loop
    while True:
        # get query
        print_header('user', 'red')
        query = prompt()

        # skip if empty
        if query.strip() == '':
            continue

        # stream reply
        print()
        print_header(name, 'blue')
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
