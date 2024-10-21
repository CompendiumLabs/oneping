// set focus on query box
function focusQuery() {
    const query = document.getElementById('query');
    query.focus();
    query.setSelectionRange(query.value.length, query.value.length);
}

// render markdown in message display
function renderBox(box) {
    const data = box.querySelector('.message-data').textContent;
    const display = box.querySelector('.message-display');
    display.innerHTML = marked.parse(data);
}

// handle websocket events - hide and show query box
document.addEventListener('htmx:wsBeforeMessage', event => {
    const message = event.detail.message;
    const query_box = document.getElementById('query-box');
    if (message == 'ONEPING_START') {
        query_box.classList.add('hidden');
    } else if (message == 'ONEPING_DONE') {
        query_box.classList.remove('hidden');
        focusQuery();
    }
});

// handle websocket events - render last message and scroll to bottom
document.addEventListener('htmx:wsAfterMessage', event => {
    const chat = document.getElementById('chat');
    const last = chat.querySelector('.chat-box:last-child > .message');
    if (last == null) return;
    renderBox(last);
    chat.scrollTop = chat.scrollHeight;
});

// render markdown in all messages and set focus on query box
document.addEventListener('DOMContentLoaded', () => {
    const chat = document.getElementById('chat');
    const boxes = chat.querySelectorAll('.chat-box > .message');
    for (const box of boxes) {
        renderBox(box);
    }
    focusQuery();
});
