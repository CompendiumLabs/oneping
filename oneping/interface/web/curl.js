// a javascript mini-library for making chat completion requests to an LLM provider

//
// constants
//

const OPENAI_MODEL = 'gpt-4o';
const ANTHROPIC_MODEL = 'claude-3-5-sonnet-latest';

//
// authorization
//

function authorize_openai(apiKey) {
    return { 'Authorization': `Bearer ${apiKey}` };
}

function authorize_anthropic(apiKey) {
    return { 'x-api-key': apiKey };
}

//
// payloads
//

function payload_openai(query, args) {
    const { system, history, prefill } = args ?? {};
    let messages = [];
    if (system != null) {
        messages.push({ role: 'system', content: system });
    }
    if (history != null) {
        messages.push(...history);
    }
    messages.push({ role: 'user', content: query });
    if (prefill != null) {
        messages.push({ role: 'assistant', content: prefill });
    }
    let payload = { messages };
    return payload;
}

function payload_anthropic(query, args) {
    const { system, history, prefill } = args ?? {};
    let messages = [];
    if (history != null) {
        messages.push(...history);
    }
    messages.push({ role: 'user', content: query });
    if (prefill != null) {
        messages.push({ role: 'assistant', content: prefill });
    }
    let payload = { messages };
    if (system != null) {
        payload.system = system;
    }
    return payload;
}

//
// extractors
//

function extractor_openai(response) {
    return response.choices[0].message.content;
}

function extractor_anthropic(response) {
    return response.content[0].text;
}

//
// providers
//

const DEFAULT_PROVIDER = {
    payload: payload_openai,
    response: extractor_openai,
}

const providers = {
    local: {
        url: port => `http://localhost:${port}/v1/chat/completions`,
    },
    openai: {
        url: _ => 'https://api.openai.com/v1/chat/completions',
        authorize: authorize_openai,
        model: { model: OPENAI_MODEL },
        max_tokens_name: 'max_completion_tokens',
    },
    anthropic: {
        url: _ => 'https://api.anthropic.com/v1/messages',
        authorize: authorize_anthropic,
        payload: payload_anthropic,
        response: extractor_anthropic,
        model: { model: ANTHROPIC_MODEL },
        extra: {
            'anthropic-version': '2023-06-01',
            'anthropic-beta': 'prompt-caching-2024-07-31',
            'anthropic-dangerous-direct-browser-access': 'true',
        },
    },
};

function get_provider(provider) {
    return { ...DEFAULT_PROVIDER, ...providers[provider] };
}

//
// reply
//

async function reply(query, args) {
    let { provider, system, history, prefill, apiKey, max_tokens, port } = args ?? {};
    apiKey = apiKey ?? get_api_key(provider);
    max_tokens = max_tokens ?? 1024;
    port = port ?? 8000;

    // get provider settings
    provider = get_provider(provider ?? 'local');

    // check authorization
    if (provider.authorize != null && apiKey == null) {
        throw new Error('API key is required');
    }

    // get request params
    const url = provider.url(port);
    const extra = provider.extra ?? {};
    const model = provider.model ?? {};
    const max_tokens_name = provider.max_tokens_name ?? 'max_tokens';
    const authorize = provider.authorize ? provider.authorize(apiKey) : {};
    const message = provider.payload(query, { system, history, prefill });

    // prepare request
    const headers = { 'Content-Type': 'application/json', ...authorize, ...extra };
    const payload = { ...message, ...model, [max_tokens_name]: max_tokens };

    // make request
    const response = await fetch(url, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(payload),
    });

    // return json data
    const data = await response.json();
    return provider.response(data);
}

//
// element creation
//

function h(tag, args, children) {
    let { style, cls, ...attrs } = args ?? {};
    children = children ?? [];

    // create element
    const elem = document.createElement(tag);

    // add classes
    if (cls != null) {
        cls = Array.isArray(cls) ? cls : [cls];
        elem.classList.add(...cls);
    }

    // add styles
    for (const [key, value] of Object.entries(style ?? {})) {
        elem.style[key] = value;
    }

    // add attributes
    for (const [key, value] of Object.entries(attrs)) {
        elem[key] = value;
    }

    // add children
    children = Array.isArray(children) ? children : [children];
    for (const child of children) {
        elem.append(child);
    }

    // return element
    return elem;
}

//
// key management
//

function get_api_key(provider) {
    return localStorage.getItem(`${provider}-api-key`);
}

function set_api_key(provider, apiKey) {
    localStorage.setItem(`${provider}-api-key`, apiKey);
}

function clear_api_key(provider) {
    localStorage.removeItem(`${provider}-api-key`);
}

function create_api_key_widget() {
    const input = h('input', {
        type: 'text', placeholder: 'API key', style: { flexGrow: 1 }
    });
    const button = h('button', { textContent: 'Store' });

    // create elements
    const outer = h('div', {
        id: 'api-key-widget',
        style: { display: 'flex', flexDirection: 'row', gap: '0.5em' },
    }, [input, button]);

    // return outer
    return outer;
}

function api_key_widget(provider) {
    // create api key widget
    const widget = create_api_key_widget();
    const input = widget.querySelector('input');
    const button = widget.querySelector('button');

    // state variable
    let api_key = get_api_key(provider);
    let is_set = api_key != null;

    // set initial button text
    if (is_set) {
        button.textContent = 'Clear';
        input.value = '*'.repeat(api_key.length);
        input.disabled = true;
    }

    // click handler
    button.onclick = () => {
        if (is_set) {
            clear_api_key(provider);
            is_set = false;
            input.value = '';
            input.disabled = false;
            button.textContent = 'Store';
        } else {
            const value = input.value;
            if (value.length > 0) {
                set_api_key(provider, value);
                is_set = true;
                input.value = '*'.repeat(value.length);
                input.disabled = true;
                button.textContent = 'Clear';

            }
        }
    }

    // return widget
    return widget;
}

//
// exports
//

export { reply, get_api_key, set_api_key, clear_api_key, api_key_widget, h };
