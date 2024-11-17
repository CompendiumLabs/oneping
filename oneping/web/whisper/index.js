// whisper

import { AudioRecorder, transcribe } from '../audio.js';
import { api_key_widget, get_api_key } from '../curl.js';

// constants
const LOCAL_PORT = 8123;
const OPENAI_URL = 'https://api.openai.com/v1/audio/transcriptions';

// url arguments
const url_args = new URLSearchParams(window.location.search);
const openai = url_args.get('openai') != null;
function get_trans_args() {
    if (openai) {
        return { url: OPENAI_URL, apiKey: get_api_key('openai') };
    } else {
        return { port: LOCAL_PORT };
    }
}

// init objects
const recorder = new AudioRecorder();

// ui objects
const output = document.getElementById('output');
const circle = document.getElementById('status');

// make a new message box
function makeMessage(timestamp, text) {
    const time = document.createElement('span');
    time.textContent = timestamp;
    time.classList.add(
        'timestamp', 'italic', 'w-[110px]', 'min-w-[110px]', 'text-center',
        'py-1', 'px-2', 'border-r', 'border-gray-300'
    );

    const content = document.createElement('span');
    content.textContent = text;
    content.classList.add('content', 'py-1', 'px-2');

    const message = document.createElement('div');
    message.classList.add(
        'message', 'flex', 'flex-row', 'border', 'rounded',
        'border-gray-300', 'bg-gray-100'
    );
    message.appendChild(time);
    message.appendChild(content);
    return message;
}

function downloadAudio(audio) {
    const url = URL.createObjectURL(audio);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'audio.wav';
    a.click();
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

// create api key widget
const widget = api_key_widget('openai');
document.body.appendChild(widget);
widget.style.display = 'none';
const api_input = widget.querySelector('input');

// handle F1 login
document.addEventListener('keydown', (event) => {
    if (event.key === 'F1') {
        const display = widget.style.display;
        if (display === 'none') {
            widget.style.display = 'flex';
            api_input.focus();
        } else {
            widget.style.display = 'none';
            document.body.focus();
        }
    }
});
