document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    const submitButton = form.querySelector("button[type='submit']");

    if (submitButton.textContent === "Registrar-se"){

        if (form && submitButton) {
            form.addEventListener("submit", function () {
                submitButton.disabled = true;
                submitButton.textContent = "Registrant-se...";
            });
        }

    } else {
        if (form && submitButton) {
            form.addEventListener("submit", function () {
                submitButton.disabled = true;
                submitButton.textContent = "Iniciant sessió...";
            });
        }
    }
});
