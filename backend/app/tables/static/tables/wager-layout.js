// Keep the preferred radial position when the complete chip label fits there.
let wagerObserver;
function bindWagerLayout() {
wagerObserver?.disconnect();
const arena = document.querySelector(".live-table");
if (arena) {
    const seats = [...arena.querySelectorAll(".table-seat")];
    const wagers = [...arena.querySelectorAll(".felt-wager")];
    const board = arena.querySelector(".board-zone");

    function positionWagers() {
        const bounds = arena.getBoundingClientRect();
        const centerX = bounds.left + bounds.width / 2;
        const centerY = bounds.top + bounds.height / 2;
        const gap = 6;
        const obstacles = [...seats, board].map(el => el.getBoundingClientRect());
        for (const wager of wagers) {
            wager.style.removeProperty("left");
            wager.style.removeProperty("top");
            const preferred = wager.getBoundingClientRect();
            const seat = wager.parentElement.querySelector(".table-seat").getBoundingClientRect();
            const seatX = seat.left + seat.width / 2;
            const seatY = seat.top + seat.height / 2;
            const seatRadius = Math.hypot(seatX - centerX, seatY - centerY);
            const fits = (x, y) => x >= bounds.left + gap && y >= bounds.top + gap &&
                x + preferred.width <= bounds.right - gap && y + preferred.height <= bounds.bottom - gap &&
                obstacles.every(o => x + preferred.width + gap <= o.left || x >= o.right + gap ||
                    y + preferred.height + gap <= o.top || y >= o.bottom + gap);

            if (!fits(preferred.left, preferred.top)) {
                let best;
                let bestCost = Infinity;
                for (let y = bounds.top + gap; y + preferred.height <= bounds.bottom - gap; y += gap) {
                    for (let x = bounds.left + gap; x + preferred.width <= bounds.right - gap; x += gap) {
                        const cost = (x - preferred.left) ** 2 + (y - preferred.top) ** 2;
                        if (cost >= bestCost || !fits(x, y)) continue;
                        if (Math.hypot(x + preferred.width / 2 - centerX,
                                       y + preferred.height / 2 - centerY) >= seatRadius) continue;
                        best = {x, y};
                        bestCost = cost;
                    }
                }
                if (best) {
                    wager.style.left = (best.x - bounds.left + preferred.width / 2) + "px";
                    wager.style.top = (best.y - bounds.top + preferred.height / 2) + "px";
                }
            }
            obstacles.push(wager.getBoundingClientRect());
        }
    }
    if (wagers.length) {
        positionWagers();
        wagerObserver = new ResizeObserver(positionWagers);
        for (const element of [arena, board, ...seats, ...wagers]) wagerObserver.observe(element);
    }
}

}
bindWagerLayout();
