document.addEventListener("DOMContentLoaded", function () {
    const select = document.getElementById("book_to_exchange");
    const previewBox = document.getElementById("user-book-preview");
    const previewTitle = document.getElementById("user-book-title");

    if (select) {
        select.addEventListener("change", function () {
            const selectedOption = this.options[this.selectedIndex];
            const imgUrl = selectedOption.getAttribute("data-img");
            const title = selectedOption.getAttribute("data-title");

            if (imgUrl) {
                previewBox.innerHTML = `<img src="${imgUrl}" alt="${title}" style="width: 100%; height: auto; border-radius: 10px;">`;
                previewTitle.textContent = title;
            } else {
                previewBox.innerHTML = `<p style="color:white; text-align:center;">Sense imatge</p>`;
                previewTitle.textContent = "Selecciona un llibre";
            }
        });
    }
});