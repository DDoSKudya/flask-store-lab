document.addEventListener("DOMContentLoaded", () => {
    const confirmForms = document.querySelectorAll(
        "form[data-confirm-message]"
    );

    for (const form of confirmForms) {
        form.addEventListener("submit", (event) => {
            const message = form.dataset.confirmMessage || "Are you sure?";
            if (!window.confirm(message)) {
                event.preventDefault();
            }
        });
    }
});
