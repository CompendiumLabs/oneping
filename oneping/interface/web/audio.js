// audio recording and transcription

// audio constants
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
function recordMediaStream(recorder) {
    return new Promise((resolve, reject) => {
        const chunks = [];
        recorder.ondataavailable = (event) => {
            chunks.push(event.data);
        };
        recorder.onstop = async (event) => {
            const blob = new Blob(chunks, { 'type' : 'audio/ogg; codecs=opus' });
            const buf = await blobToUint8Array(blob);
            resolve(buf);
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
    async startRecording(max_length=DEFAULT_MAX_LENGTH) {
        if (this.context == null) {
            this.initContext();
        }

        // record media stream to array of uint8 data
        const stream = await navigator.mediaDevices.getUserMedia({audio: true, video: false});
        const recorder = new MediaRecorder(stream);

        // start recording
        const startTime = Date.now();
        this.doRecording = true;

        // set up recording and termination
        const recording = recordMediaStream(recorder);
        const terminate = waitThen(
            () => !this.doRecording || getElapsedTime(startTime) > max_length,
            () => recorder.stop()
        );
        const [buffer, _] = await Promise.all([recording, terminate]);

        // end recording
        this.doRecording = false;
        console.log(`recorded for ${getElapsedTime(startTime).toFixed(2)} seconds`);

        // decode audio data
        const audioBuffer = await this.context.decodeAudioData(buffer.buffer);
        const audio = audioBuffer.getChannelData(0);
        console.log(`recorded audio size: ${audio.length}`);

        // return audio
        return audio;
    }
}

export { AudioRecorder };
