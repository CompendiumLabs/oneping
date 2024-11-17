// storage

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

//
// widget
//

function h(tag, args, children) {
    let { style, cls, ...attrs } = args ?? {};
    children = children ?? [];

    // create element
    const elem = document.createElement(tag);

    // add classes
    if (cls != null) {
        cls = Array.isArray(cls) ? cls : cls.split(' ');
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

function create_api_key_widget() {
    const input = h('input', {
        type: 'text', placeholder: 'Enter your API key', style: { flexGrow: 1 }
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

export { get_api_key, set_api_key, clear_api_key, api_key_widget, h };
