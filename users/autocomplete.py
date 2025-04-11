from dal import autocomplete
from cities_light.models import City

class CityAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Asegurarse de que el usuario esté autenticado
        if not self.request.user.is_authenticated:
            return City.objects.none()

        # Obtener todas las ciudades
        qs = City.objects.all()

        # Filtrar por el término de búsqueda
        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs