let busy = false;

// Keep the audio context alive across human moves and automatic bot steps.
document.addEventListener("submit", async event => {
    const form = event.target;
    const table = form.closest("main.table-page");
    if (!table || form.method !== "post") return;
    event.preventDefault();
    if (busy) return;
    busy = true;
    try {
        const data = new FormData(form);
        if (event.submitter?.name) data.set(event.submitter.name, event.submitter.value);
        // Wager buttons are named "action", which shadows form.action.
        const response = await fetch(form.getAttribute("action"), {
            method: "POST", body: data, headers: {"X-Table-Update": "1"}
        });
        if (!response.ok) throw new Error("Table update failed");
        const doc = new DOMParser().parseFromString(await response.text(), "text/html");
        const updated = doc.querySelector("main.table-page");
        if (!updated) throw new Error("Missing table");
        table.replaceWith(updated);
        bindBettingControls(playCue(response.headers.get("X-Poker-Sound")));
        bindWagerLayout();
    } catch {
        // Reload the saved state without resubmitting a possibly committed action.
        location.reload();
    } finally {
        busy = false;
    }
});
