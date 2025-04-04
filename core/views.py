from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from books.models import Book, Exchange, Category
from users.models import Notification
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import QueryDict

# Create your views here.


def index(request):
    categories = {
        "Novel·la": Book.objects.filter(category_id=1),  # ID real de cada categoría
        "Acció": Book.objects.filter(category_id=2),
        "Educació": Book.objects.filter(category_id=3),
        "Fantasia": Book.objects.filter(category_id=4),
        "Ciència Ficció": Book.objects.filter(category_id=5)
    }
    
    return render(request, 'index.html', {
        'categories': categories
    })

@login_required
def dashboard(request):
    # Obtener los parámetros de búsqueda
    title = request.GET.get('title', '').strip()
    author = request.GET.get('author', '').strip()
    category_id = request.GET.get('category', '').strip()

    # Filtrar libros del usuario
    books = Book.objects.filter(owner=request.user)

    # Aplicar filtros si se proporcionan
    if title:
        books = books.filter(Q(title__icontains=title) | Q(isbn__icontains=title))
    if author:
        books = books.filter(author__icontains=author)
    if category_id:
        books = books.filter(category_id=category_id)

    # Paginación
    paginator = Paginator(books, 3)  # Mostrar 9 libros por página
    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)

    # Ranking de libros más intercambiados
    ranking = (
        Book.objects.filter(
            Q(exchanges_given__completed=True) | Q(exchanges_received__completed=True)
        )
        .values('title')
        .annotate(exchange_count=Count('exchanges_given') + Count('exchanges_received'))
        .order_by('-exchange_count')[:5]
    )

    # Novedades (últimos libros añadidos)
    new_books = Book.objects.filter(visible=True).order_by('-created_at')[:3]

    # Categorías para los filtros
    categories = Category.objects.all()

    # Copiar los parámetros GET
    query_params = request.GET.copy()

    # Eliminar el parámetro 'page' si existe
    query_params.pop('page', None)

    # Pasar los parámetros restantes al contexto
    context = {
        'books': books,
        'ranking': ranking,
        'new_books': new_books,
        'categories': categories,
        'query_params': query_params.urlencode(),  # Parámetros GET sin 'page'
    }

    return render(request, 'user.dashboard.html', context)