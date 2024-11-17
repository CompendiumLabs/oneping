// whisper

import { AudioRecorder, transcribe, OPENAI_URL, LOCAL_URL } from '../audio.js';
import { api_key_widget, get_api_key, h } from '../storage.js';

// init objects
const recorder = new AudioRecorder();

// ui objects
const output = document.getElementById('output');
const circle = document.getElementById('status');

// make a new message box
function makeMessage(timestamp, text) {
    const time = h('span', { cls: [
        'timestamp', 'italic', 'w-[110px]', 'min-w-[110px]', 'text-center',
        'py-1', 'px-2', 'border-r', 'border-gray-300'
    ] }, timestamp);
    const content = h('span', { cls: ['content', 'py-1', 'px-2'] }, text);
    const message = h('div', { cls: [
        'message', 'flex', 'flex-row', 'border', 'rounded',
        'border-gray-300', 'bg-gray-100'
    ] }, [time, content]);
    return message;
}

// get transcription arguments
function get_trans_args() {
    const host = localStorage.getItem('whisper-host');
    const api_key = get_api_key('openai');
    return { url: host, apiKey: api_key };
}

// record action
let recording = false;
document.addEventListener('keydown', async (event) => {
    if (!recording && event.key == ' ') {
        // go to recording state
        recording = true;
        const timestamp = new Date().toLocaleTimeString();

        // record audio
        circle.classList.add('recording');
        const audio = await recorder.startRecording({ decode: false });
        circle.classList.remove('recording');

        if (audio != null) {
            // transcribe audio
            circle.classList.add('transcribing');
            const text = await transcribe(audio, get_trans_args());
            console.log(`transcribe: ${text}`);
            circle.classList.remove('transcribing');

            // display text
            const message = makeMessage(timestamp, text);
            output.appendChild(message);
            output.scrollTop = output.scrollHeight;
        }

        // back to normal state
        recording = false;
    }
});

document.addEventListener('keyup', async (event) => {
    if (recording && event.key == ' ') {
        recorder.stopRecording();
    }
});

//
// configuration
//

// get ui elements
const control = document.getElementById('control');
const api_key = control.querySelector('#api-key > .control-input');
const host_input = control.querySelector('#host-input');
const host_button = control.querySelector('#host-button');

// create api key widget
const widget = api_key_widget('openai');
api_key.appendChild(widget);

// set host from storage
const host_initial = localStorage.getItem('whisper-host');
host_input.value = host_initial ?? OPENAI_URL;
if (host_initial == OPENAI_URL) {
    host_button.textContent = 'Local';
} else {
    host_button.textContent = 'OpenAI';
}

// handle F1 toggle
document.addEventListener('keydown', (event) => {
    if (event.key === 'F1') {
        const display = control.style.display;
        if (display === 'none') {
            control.style.display = 'flex';
            api_key.focus();
        } else {
            control.style.display = 'none';
            document.body.focus();
        }
    }
});

// handle set openai
host_button.addEventListener('click', () => {
    const label = host_button.textContent;
    if (label == 'OpenAI') {
        host_input.value = OPENAI_URL;
        host_button.textContent = 'Local';
    } else {
        host_input.value = LOCAL_URL;
        host_button.textContent = 'OpenAI';
    }
    const host = host_input.value;
    localStorage.setItem('whisper-host', host);
});

// handle host input
host_input.addEventListener('input', () => {
    const host = host_input.value;
    localStorage.setItem('whisper-host', host);
});
