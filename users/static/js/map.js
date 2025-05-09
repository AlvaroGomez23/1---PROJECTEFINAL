document.addEventListener('DOMContentLoaded', function () {
    const lat = parseFloat(document.getElementById('map').dataset.lat);
    const lng = parseFloat(document.getElementById('map').dataset.lng);
    const radiusKm = parseFloat(document.getElementById('map').dataset.radius);
    const radius = radiusKm * 1000;
    const username = document.getElementById('user').textContent;
   

    if (!isNaN(lat) && !isNaN(lng) && radius > 0) {
        const map = L.map('map').setView([lat, lng], 13);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors'
        }).addTo(map);

        L.marker([lat, lng])
            .addTo(map)
            .bindPopup("Radi de moviment de " + username);

        L.circle([lat, lng], {
            color: 'green',
            fillColor: '#0f0',
            fillOpacity: 0.3,
            radius: radius
        }).addTo(map).bindPopup(`Radi de moviment: ${radiusKm} km`);

        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                function (position) {
                    const userLat = position.coords.latitude;
                    const userLng = position.coords.longitude;

                    L.marker([userLat, userLng], { color: 'blue' })
                        .addTo(map)
                        .bindPopup("La teva ubicació actual")
                        .openPopup();

                    const bounds = L.latLngBounds([[lat, lng], [userLat, userLng]]);
                    map.fitBounds(bounds);
                },
                function (error) {
                    console.error("Error obtenint la ubicació actual:", error.message);
                }
            );
        } else {
            console.error("Geolocalització no suportada pel navegador.");
        }
    } else {
        document.getElementById('map').innerHTML = '<p class="error";">No s\' ha pogut carregar el mapa.</p>';
    }
});
