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
// exports
//

export { reply };
