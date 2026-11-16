const form = document.querySelector("#betting-controls");

if (form) {
    const amount = form.querySelector("#amount");
    const slider = form.querySelector("#slider");
    const wagerTotal = form.querySelector("#wager-total");

    if (amount && slider && wagerTotal) {
        function setWager(value) {
            const minimum = Number(amount.min);
            const maximum = Number(amount.max);
            const total = Math.min(maximum, Math.max(minimum, Math.round(value)));

            amount.value = total;
            slider.value = total;
            wagerTotal.textContent = total.toLocaleString();
        }

        slider.addEventListener("input", () => {
            setWager(slider.valueAsNumber);
        });

        amount.addEventListener("input", () => {
            // Let the player finish typing a multi-digit amount.
            if (amount.validity.valid) {
                slider.value = amount.value;
                wagerTotal.textContent = amount.valueAsNumber.toLocaleString();
            } else {
                wagerTotal.textContent = "…";
            }
        });

        for (const preset of form.querySelectorAll("[data-size]")) {
            preset.addEventListener("click", () => {
                if (preset.dataset.size === "all") {
                    setWager(Number(amount.max));
                    return;
                }

                const pot = Number(form.dataset.pot);
                const call = Number(form.dataset.call);
                const committed = Number(form.dataset.committed);
                const fraction = Number(preset.dataset.size);

                const potAfterCall = pot + call;
                const totalAfterCall = committed + call;
                setWager(totalAfterCall + fraction * potAfterCall);
            });
        }
    }

    document.addEventListener("keydown", (event) => {
        if (event.defaultPrevented || event.repeat || event.isComposing ||
            event.ctrlKey || event.metaKey || event.altKey || event.shiftKey) {
            return;
        }
        if (event.target.isContentEditable ||
            event.target.closest("input, textarea, select, button, a, dialog")) {
            return;
        }

        const key = event.key.toLowerCase();
        if (!["f", "c", "r"].includes(key)) return;

        const button = form.querySelector(`[data-key="${key}"]`);
        if (button) {
            event.preventDefault();
            button.click();
        }
    });
}

const advanceForm = document.querySelector("#advance-table");

if (advanceForm) {
    const timer = window.setTimeout(() => {
        advanceForm.requestSubmit();
    }, Number(advanceForm.dataset.delay));

    advanceForm.addEventListener("submit", () => {
        window.clearTimeout(timer);
    }, { once: true });
}