// audio recording and transcription

// audio constants
const DEFAULT_FORMAT = 'audio/ogg; codecs=opus';
const DEFAULT_MAX_LENGTH = 60;
const DEFAULT_ARGS = {
    sampleRate: 16000,
    channelCount: 1,
    echoCancellation: false,
    autoGainControl:  true,
    noiseSuppression: true,
}

// poll until condition is true
function waitUntil(condition, polling=100) {
    return new Promise((resolve, reject) => {
        const interval = setInterval(() => {
            if (condition()) {
                clearInterval(interval);
                resolve();
            }
        }, polling);
    });
}

async function waitThen(condition, then, polling=100) {
    await waitUntil(condition, polling);
    return then();
}

// blob to uint8 array
async function blobToUint8Array(blob) {
    const arrayBuffer = await blob.arrayBuffer();
    return new Uint8Array(arrayBuffer);
}

// record media stream to uint8 array
function recordMediaStream(recorder, format) {
    return new Promise((resolve, reject) => {
        const chunks = [];
        recorder.ondataavailable = (event) => {
            chunks.push(event.data);
        };
        recorder.onstop = async (event) => {
            const blob = new Blob(chunks, { type : format });
            resolve(blob);
        };
        recorder.start();
    });
}

function getElapsedTime(startTime) {
    return (Date.now() - startTime) / 1000;
}

// audio recorder interface
class AudioRecorder {
    constructor(args) {
        this.args = args ?? DEFAULT_ARGS;
        this.context = null;
        this.doRecording = false;
    }

    initContext(args) {
        args = args ?? {};
        const args1 = {...this.args, ...args};
        this.context = new AudioContext(args1);
    }

    // tell loop to stop recording
    stopRecording() {
        this.doRecording = false;
    }

    // record up to kMaxRecording_s seconds of audio from the microphone check if doRecording
    // is false every 1000 ms and stop recording if so update progress information
    async startRecording(args) {
        let { decode, max_length, format } = args ?? {};
        decode = decode ?? true;
        max_length = max_length ?? DEFAULT_MAX_LENGTH;
        format = format ?? DEFAULT_FORMAT;

        // init context on first use
        if (this.context == null) {
            this.initContext();
        }

        // record media stream to array of uint8 data
        const stream = await navigator.mediaDevices.getUserMedia({audio: true, video: false});
        const recorder = new MediaRecorder(stream, { mimeType: format });

        // start recording
        const startTime = Date.now();
        this.doRecording = true;

        // set up recording and termination
        const recording = recordMediaStream(recorder, format);
        const terminate = waitThen(
            () => !this.doRecording || getElapsedTime(startTime) > max_length,
            () => recorder.stop()
        );
        const [blob, _] = await Promise.all([recording, terminate]);

        // end recording
        this.doRecording = false;
        console.log(`recorded for ${getElapsedTime(startTime).toFixed(2)} seconds`);

        // maybe decode audio data
        if (decode) {
            const array = await blobToUint8Array(blob);
            const buffer = await this.context.decodeAudioData(array.buffer);
            return buffer.getChannelData(0);
        } else {
            return blob;
        }
    }
}

//
// requests
//

const DEFAULT_MODEL = 'whisper-1';
const OPENAI_URL = 'https://api.openai.com/v1/audio/transcriptions';
const LOCAL_URL = 'http://localhost:8000/inference';

// audio should be a Blob object
async function transcribe(audio, args) {
    let { url, apiKey, model, ...extra } = args ?? {};
    url = url ?? LOCAL_URL;

    // baseline headers and payload
    const headers = {};
    const body = new FormData();
    body.append('file', audio, 'audio.ogg');
    for (const [key, value] of Object.entries(extra)) {
        body.append(key, value);
    }

    // going proprietary
    if (apiKey != null) {
        headers['Authorization'] = `Bearer ${apiKey}`;
        body.append('model', model ?? DEFAULT_MODEL);
    }

    // make request and return text
    const response = await fetch(url, { method: 'POST', headers, body });
    const data = await response.json();
    return data.text ?? data.error;
}

export { AudioRecorder, waitUntil, waitThen, transcribe, OPENAI_URL, LOCAL_URL };
