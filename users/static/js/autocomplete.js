document.addEventListener('DOMContentLoaded', function () {
    const citySearchInput = document.getElementById('city-search');
    const resultsContainer = document.getElementById('city-results');
    const cityHiddenInput = document.getElementById('id_city');

    citySearchInput.addEventListener('input', async function () {
        const query = citySearchInput.value.trim();

        if (query.length > 1) {
            try {
                const response = await fetch(citySearchInput.dataset.autocompleteUrl + "?term=" + encodeURIComponent(query));
                if (!response.ok) throw new Error('Error al fer la petició');
                const data = await response.json();

                resultsContainer.innerHTML = '';

                if (data.length > 0) {
                    resultsContainer.style.display = 'block';

                    data.forEach(city => {
                        const listItem = document.createElement('li');
                        listItem.classList.add('list-group-item');
                        listItem.textContent = city.name;
                        listItem.dataset.id = city.id;
                        resultsContainer.appendChild(listItem);
                    });
                } else {
                    resultsContainer.innerHTML = '<li class="list-group-item">No s\' han trobat ciutats</li>';
                    resultsContainer.style.display = 'block';
                }
            } catch (error) {
                console.error(error);
            }
        } else {
            resultsContainer.innerHTML = '';
            resultsContainer.style.display = 'none';
        }
    });

    resultsContainer.addEventListener('click', function (event) {
        if (event.target && event.target.nodeName === 'LI') {
            const cityName = event.target.textContent;
            const cityId = event.target.dataset.id;
            citySearchInput.value = cityName;
            cityHiddenInput.value = cityId;
            resultsContainer.innerHTML = '';
            resultsContainer.style.display = 'none';
            console.log(`Ciutat seleccionada: ${cityName} (ID: ${cityId})`);
        }
    });
});
