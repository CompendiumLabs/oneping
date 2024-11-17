// whisper

import { AudioRecorder, transcribe } from '../audio.js';

// constants
const API_ARGS = {
    port: 8123,
};

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
            const text = await transcribe(audio, API_ARGS);
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

