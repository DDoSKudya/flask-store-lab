const isSupportedField = (field) =>
    field instanceof HTMLInputElement ||
    field instanceof HTMLSelectElement ||
    field instanceof HTMLTextAreaElement;

const applyFieldValidationState = (field) => {
    if (!isSupportedField(field)) {
        return;
    }
    if (!field.value && !field.required) {
        field.classList.remove("is-valid");
        field.classList.remove("is-invalid");
        return;
    }
    field.classList.toggle("is-valid", field.checkValidity());
    field.classList.toggle("is-invalid", !field.checkValidity());
};

const bindFieldLiveValidation = (field) => {
    field.addEventListener("input", () => applyFieldValidationState(field));
    field.addEventListener("blur", () => applyFieldValidationState(field));
};

const updateSubmitButtonState = (form) => {
    const submitButton = form.querySelector('button[type="submit"]');
    if (!(submitButton instanceof HTMLButtonElement)) {
        return;
    }
    submitButton.disabled = !form.checkValidity();
};

const handleValidationFormSubmit = (event, form, fields) => {
    if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
    }
    form.classList.add("was-validated");
    for (const field of fields) {
        applyFieldValidationState(field);
    }
    updateSubmitButtonState(form);
};

const initValidationForms = () => {
    const validationForms = document.querySelectorAll(".needs-validation");
    for (const form of validationForms) {
        const fields = form.querySelectorAll("input, select, textarea");
        for (const field of fields) {
            bindFieldLiveValidation(field);
            field.addEventListener("input", () =>
                updateSubmitButtonState(form),
            );
            field.addEventListener("blur", () => updateSubmitButtonState(form));
        }
        updateSubmitButtonState(form);
        form.addEventListener("submit", (event) =>
            handleValidationFormSubmit(event, form, fields),
        );
    }
};

const shouldSkipGenericConfirm = (form) =>
    form.classList.contains("js-delete-product-form");

const getConfirmMessage = (form, fallback) =>
    form.dataset.confirmMessage || fallback;

const initConfirmForms = () => {
    const confirmForms = document.querySelectorAll(
        "form[data-confirm-message]",
    );
    for (const form of confirmForms) {
        form.addEventListener("submit", (event) => {
            if (shouldSkipGenericConfirm(form)) {
                return;
            }
            if (!window.confirm(getConfirmMessage(form, "Are you sure?"))) {
                event.preventDefault();
            }
        });
    }
};

const sendDeleteRequest = async (form) =>
    fetch(form.action, { method: "DELETE" });

const handleDeleteResponse = (response) => {
    if (response.redirected) {
        window.location.href = response.url;
        return;
    }
    window.location.reload();
};

const initDeleteForms = () => {
    const deleteForms = document.querySelectorAll(".js-delete-product-form");
    for (const form of deleteForms) {
        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            if (
                !window.confirm(getConfirmMessage(form, "Delete this product?"))
            ) {
                return;
            }
            const response = await sendDeleteRequest(form);
            handleDeleteResponse(response);
        });
    }
};

const closeAlertElement = (alertElement) => {
    if (typeof bootstrap !== "undefined" && bootstrap.Alert) {
        bootstrap.Alert.getOrCreateInstance(alertElement).close();
        return;
    }
    alertElement.remove();
};

const initFlashAutoDismiss = () => {
    const flashAlerts = document.querySelectorAll(".js-auto-dismiss-alert");
    for (const alertElement of flashAlerts) {
        window.setTimeout(() => {
            closeAlertElement(alertElement);
        }, 3000);
    }
};

const initApp = () => {
    initValidationForms();
    initConfirmForms();
    initDeleteForms();
    initFlashAutoDismiss();
};

document.addEventListener("DOMContentLoaded", initApp);
