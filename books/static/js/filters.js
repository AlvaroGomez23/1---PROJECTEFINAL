document.addEventListener('DOMContentLoaded', function () {
    const toggleBtn = document.getElementById('toggleFiltersBtn');
    const filtersPanel = document.getElementById('filtersPanel');

    // Ocultar filtros inicialmente en pantallas pequeñas
    if (window.innerWidth < 768) {
        filtersPanel.classList.add('d-none');
        toggleBtn.textContent = 'Mostrar Filtres';
    }

    toggleBtn.addEventListener('click', function () {
        filtersPanel.classList.toggle('d-none');
        toggleBtn.textContent = filtersPanel.classList.contains('d-none') ? 'Mostrar Filtres' : 'Amagar Filtres';
    });

    // Ajustar si cambia el tamaño de pantalla
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