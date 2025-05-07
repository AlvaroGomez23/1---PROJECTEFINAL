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

    const toggleFiltersBtn = document.getElementById('toggleFiltersBtn');
    const filtersPanel = document.getElementById('filtersPanel');

    filtersPanel.addEventListener('show.bs.collapse', () => {
        toggleFiltersBtn.innerHTML = 'Amagar Filtres'; // Cambiar el texto cuando el panel se muestra
    });

    filtersPanel.addEventListener('hide.bs.collapse', () => {
        toggleFiltersBtn.innerHTML = 'Mostrar Filtres'; // Cambiar el texto cuando el panel se oculta
    });
});