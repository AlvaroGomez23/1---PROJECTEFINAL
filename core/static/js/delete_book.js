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

    const toggleBtn = document.getElementById('toggleFiltersBtn');
    const filtersPanel = document.getElementById('filtersPanel');

    // Ocultar els filtres si esta en mòbil
    if (window.innerWidth < 768) {
        filtersPanel.classList.add('d-none');
        toggleBtn.textContent = 'Mostrar Filtres';
    }

    toggleBtn.addEventListener('click', function () {
        filtersPanel.classList.toggle('d-none');
        toggleBtn.textContent = filtersPanel.classList.contains('d-none') ? 'Mostrar Filtres' : 'Amagar Filtres';
    });

    // Ajustar si cambia el tamany
    window.addEventListener('resize', function () {
        if (window.innerWidth >= 768) {
            filtersPanel.classList.remove('d-none');
            toggleBtn.textContent = 'Amagar Filtres';
        } else {
            filtersPanel.classList.add('d-none');
            toggleBtn.textContent = 'Mostrar Filtres';
        }
    });

    const form = document.getElementById('filtersForm'); 
    const submitBtn = document.getElementById('submitFilters');

    let allowSubmit = false;

    
    submitBtn.addEventListener('click', function (e) {
        allowSubmit = true;
    });

    
    form.addEventListener('submit', function (e) {
        if (!allowSubmit) {
            e.preventDefault(); 
            console.warn("Bloqueado envío automático no deseado");
        }
        allowSubmit = false; 
    });
});