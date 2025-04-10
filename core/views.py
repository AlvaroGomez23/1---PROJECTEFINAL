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
    # Obtener los libros del usuario actual
    books = Book.objects.filter(owner=request.user)

    # Paginación para los libros del usuario
    paginator = Paginator(books, 3)  # Mostrar 6 libros por página
    page_number = request.GET.get('page')
    books_page = paginator.get_page(page_number)

    # Obtener los libros más intercambiados
    ranking = Book.objects.filter(exchange_count__gt=0).order_by('-exchange_count')[:4]

    # Obtener las novedades (últimos libros creados)
    new_books = Book.objects.order_by('-created_at')[:4]

    # Obtener categorías para los filtros
    categories = Category.objects.all()

    # Parámetros de búsqueda
    title = request.GET.get('title', '')
    author = request.GET.get('author', '')
    category = request.GET.get('category', '')

    # Filtrar libros del usuario
    if title:
        books = books.filter(title__icontains=title)
    if author:
        books = books.filter(author__icontains=author)
    if category:
        books = books.filter(category_id=category)

    return render(request, 'user.dashboard.html', {
        'books': books_page,  # Pasar la página actual de libros
        'ranking': ranking,
        'new_books': new_books,
        'categories': categories,
        'query_params': f"title={title}&author={author}&category={category}",
    })