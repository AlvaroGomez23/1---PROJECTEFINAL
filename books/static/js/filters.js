document.addEventListener('DOMContentLoaded', function () {
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
});