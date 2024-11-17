// client-side chat interface

import { reply, api_key_widget, get_api_key, h } from '../curl.js';

//
// constants
//

const provider = 'anthropic';
const system_prompt = 'You are a helpful assistant that loves to use emojis.';

// components
//

function make_message(role, content, system = false) {
    const system_cls = system ? ['message-system'] : [];
    return h('div', { cls: 'message-box' }, [
        h('div', { cls: 'message-role' }, h('span', {}, role)),
        h('div', { cls: ['message-content', ...system_cls] }, content),
    ]);
}

//
// message send
//

// get ui elements
const chat = document.querySelector('#chat');
const query_box = document.querySelector('#query-box');
const query = document.querySelector('#query');

// create api key widget
const widget = api_key_widget(provider);
document.body.appendChild(widget);
widget.style.display = 'none';
const api_input = widget.querySelector('input');

// handle keypress
query.addEventListener('keypress', async (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
        // prevent default
        event.preventDefault();

        // get query value
        const query_value = query.value;

        // insert query into chat
        const sent = make_message('user', query_value);
        chat.insertBefore(sent, query_box);

        // clear query
        query.value = '';

        // get api key
        const api_key = get_api_key(provider);

        // get response
        const response = await reply(query_value, { provider, system: system_prompt, apiKey: api_key });

        // add response to chat
        const message = make_message('assistant', response);
        chat.insertBefore(message, query_box);
    }
});

// handle F1 login
document.addEventListener('keydown', (event) => {
    if (event.key === 'F1') {
        // toggle visibility
        const display = widget.style.display;
        if (display === 'none') {
            widget.style.display = 'flex';
            api_input.focus();
        } else {
            widget.style.display = 'none';
            query.focus();
        }
    }
});

//
// main
//

// prepend system message
const system = make_message('system', system_prompt, true);
chat.insertBefore(system, query_box);

// set focus
query.focus();
