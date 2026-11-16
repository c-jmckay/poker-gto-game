const setup = document.querySelector(".setup-controls");
const seats = document.querySelectorAll("[data-bot]");
const start = setup.querySelector(".setup-start");

function updatePreview() {
    const bots = Number(setup.elements.bot_count.value);
    document.querySelector("#seat-count").textContent = (bots + 1) + " players";
    seats.forEach((seat, index) => {
        seat.hidden = index >= bots;
        if (seat.hidden) return;
        const angle = Math.PI / 2 + 2 * Math.PI * (index + 1) / (bots + 1);
        seat.style.left = (50 + 38 * Math.cos(angle)) + "%";
        seat.style.top = (50 + 34 * Math.sin(angle)) + "%";
    });
}

setup.addEventListener("change", updatePreview);
setup.addEventListener("submit", event => {
    if (start.disabled) {
        event.preventDefault();
        return;
    }
    start.disabled = true;
    start.textContent = "Starting…";
});
window.addEventListener("pageshow", () => {
    start.disabled = false;
    start.textContent = "Start game";
    updatePreview();
});
updatePreview();
