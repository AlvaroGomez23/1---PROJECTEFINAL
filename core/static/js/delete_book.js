document.addEventListener("DOMContentLoaded", function () {
    const deleteModal = document.getElementById("deleteModal");
    if (deleteModal) {
        deleteModal.addEventListener("show.bs.modal", function (event) {
            const button = event.relatedTarget; // Botón que abrió el modal
            const bookId = button.getAttribute("data-book-id"); // Obtener el ID del libro
            const bookTitle = button.getAttribute("data-book-title"); // Obtener el título del libro

            // Actualizar el contenido del modal
            const modalBookTitle = document.getElementById("modalBookTitle");
            modalBookTitle.textContent = bookTitle;

            const modalBookId = document.getElementById("modalBookId");
            modalBookId.textContent = bookId;

            // Actualizar la acción del formulario
            const deleteForm = document.getElementById("deleteForm");
            deleteForm.action = deleteForm.action.replace(/\/\d+\/$/, `/${bookId}/`);
        });
    }
});