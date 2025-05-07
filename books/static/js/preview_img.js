document.addEventListener("DOMContentLoaded", function () {
    const imageInput = document.getElementById("id_image");
    if (imageInput) {
        imageInput.addEventListener("change", function (event) {
            const preview = document.querySelector(".image-preview");
            const file = event.target.files[0];

            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    preview.innerHTML = '<img src="' + e.target.result + '" alt="Previsualització" class="img-fluid">';
                };
                reader.readAsDataURL(file);
            } else {
                preview.innerHTML = "<span>No s'ha seleccionat cap imatge</span>";
            }
        });
    }
});