const soundToggle = document.querySelector("#table-sound");
const buffers = new Map();
let enabled = localStorage.getItem("poker-sound") === "on";
let audio;


function showSoundPreference() {
    soundToggle.title = enabled ? "Mute sound" : "Unmute sound";
    soundToggle.setAttribute("aria-pressed", String(enabled));
}

function unlockAudio() {
    if (!enabled) return;
    audio ??= new AudioContext();
    if (audio.state !== "running") audio.resume().catch(() => {});
}

async function playCue(cue) {
    if (!enabled) return;
    if (cue === "flip") {
        const clip = document.querySelector("#deal-flip");
        clip.currentTime = 0;
        await clip.play().catch(() => {});
        return;
    }
    if (!audio || !soundToggle.dataset[cue]) return;
    try {
        if (!buffers.has(cue)) {
            buffers.set(cue, fetch(soundToggle.dataset[cue], {signal: AbortSignal.timeout(2000)})
                .then(response => response.arrayBuffer())
                .then(bytes => audio.decodeAudioData(bytes)));
        }
        const buffer = await buffers.get(cue);
        if (!enabled || audio.state !== "running") return;
        const source = audio.createBufferSource();
        source.buffer = buffer;
        source.connect(audio.destination);
        await new Promise(resolve => {
            // A muted or interrupted audio context may stop its clock.
            const fallback = setTimeout(finish, buffer.duration * 1000 + 150);
            audio.addEventListener("statechange", interrupted);
            function interrupted() {
                if (audio.state !== "running") finish();
            }
            function finish() {
                source.onended = null;
                source.disconnect();
                clearTimeout(fallback);
                audio.removeEventListener("statechange", interrupted);
                resolve();
            }
            source.onended = finish;
            source.start();
        });
    } catch {
        buffers.delete(cue);
    }
}

soundToggle.addEventListener("click", () => {
    enabled = !enabled;
    localStorage.setItem("poker-sound", enabled ? "on" : "off");
    if (enabled) unlockAudio();
    else {
        audio?.suspend().catch(() => {});
        document.querySelector("#deal-flip")?.pause();
    }
    showSoundPreference();
});
document.addEventListener("pointerdown", unlockAudio);
document.addEventListener("keydown", unlockAudio);
showSoundPreference();

const clickAudio = document.querySelector("#button-click");
let lastClick = Promise.resolve();

document.addEventListener("click", event => {
    const target = event.target.closest("button, .count-picker input, a.outline");
    if (!enabled || !target || target.matches(":disabled")) return;
    clickAudio.currentTime = 0;
    lastClick = clickAudio.play().then(() => new Promise(resolve => {
        clickAudio.addEventListener("ended", resolve, {once: true});
    })).catch(() => {});

    // A full navigation would cut the short clip off.
    if (target.matches("a.outline") && !event.metaKey && !event.ctrlKey &&
        !event.shiftKey && !event.altKey && event.button === 0) {
        event.preventDefault();
        afterButtonClick(() => location.assign(target.href));
    }
});

function afterButtonClick(callback) {
    Promise.race([lastClick, new Promise(resolve => setTimeout(resolve, 250))])
        .then(callback);
}
