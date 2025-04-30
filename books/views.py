from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from .models import Book, Exchange, Category, Review
from users.models import Wishlist, Notification
from .forms import createBook, ExchangeForm
from django.contrib.auth.decorators import login_required
from users.utils import send_user_notification
from django.db.models import Avg
from django.contrib import messages


# Create your views here.

def books(request):
    # Filtrar solo libros visibles
    books = Book.objects.filter(visible=True).exclude(owner=request.user)
    categories = Category.objects.all()
    user_wishlist = Wishlist.objects.filter(user=request.user).first()
    # Obtener parámetros de consulta
    title_or_isbn = request.GET.get('title', '')  # Usar el mismo campo para título e ISBN
    author = request.GET.get('author', '')
    min_price = request.GET.get('min_price', None)
    max_price = request.GET.get('max_price', None)
    category = request.GET.get('category', '')

    # Filtrar por título o ISBN
    if title_or_isbn:
        books = books.filter(title__icontains=title_or_isbn) | books.filter(isbn__icontains=title_or_isbn)

    # Filtrar por autor
    if author:
        books = books.filter(author__icontains=author)

    # Filtrar por rango de precios
    if min_price:
        books = books.filter(price__gte=min_price)
    if max_price:
        books = books.filter(price__lte=max_price)

    # Filtrar por categoría
    if category:
        books = books.filter(category__name=category)

    exchanges_pending = {
        book.id: Exchange.objects.filter(
            book_for=book,
            from_user=request.user,
            completed=False,
            declined=False
        ).exists()
        for book in books
    }

    return render(request, 'books.html', {
        'books': books,
        'exchanges_pending': exchanges_pending,
        'user_wishlist': user_wishlist,
        'categories': categories
    })


def book_details(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    reviews = book.book_reviews_recieved.all()
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    context = {
        'book': book,
        'reviews': reviews,
        'average_rating': average_rating,
    }
    return render(request, 'book_details.html', context)



def check_isbn_in_wishlists(isbn):
    wishlists = Wishlist.objects.filter(desired_isbns__contains=isbn)
    for wishlist in wishlists:
        # Si se encuentra el ISBN en la wishlist de algún usuario, enviar una notificación
        user = wishlist.user
        title = f"¡Un libro que deseas está disponible!"
        message = f"El libro con ISBN {isbn} que tenías en tu wishlist ahora está disponible."
        
        # Enviar la notificación
        send_user_notification(user, None, title, message, None)


@login_required
def create_book(request):
    if request.method == 'GET':
        form = createBook()
        return render(request, 'create_book.html', {'form': form})
    
    else:
        form = createBook(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.owner = request.user
            book.save()
            
            return redirect('book_details', book_id=book.pk)
        else:
            print("Error al crear el llibre")
            print(form.errors)


        return render(request, 'create_book.html', {'form': form})
    

@login_required
def modify_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    
    # Verifica si el usuario actual es el propietario del libro
    if book.owner != request.user:
        return redirect('books')  # Redirige a la lista de libros si no es el propietario

    if request.method == 'GET':
        form = createBook(instance=book)
        return render(request, 'modify_book.html', {
            'form': form,
            'book': book
        })
    
    else:
        form = createBook(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_details', book_id=book.pk)
        
        return render(request, 'modify_book.html', {'form': form})
    

def new_books(request):
    books = Book.objects.order_by('-created_at')[:10]  # Últimos 10 libros
    user_wishlist = Wishlist.objects.filter(user=request.user).first()  # Obtener la wishlist del usuario
    return render(request, 'new_books.html', {
        'books': books,
        'user_wishlist': user_wishlist,  # Pasar la wishlist al contexto
    })


@login_required
def request_exchange(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    
    if book.owner == request.user:
        return redirect('books')  # No puedes solicitar un intercambio con tu propio libro
    
    # Verificar si ya existe un intercambio pendiente entre estos usuarios y libros
    existing_exchange = Exchange.objects.filter(
        book_for=book,
        book_from__in=Book.objects.filter(owner=request.user),
        from_user=request.user,
        to_user=book.owner,
        completed=False,
        declined=False,
        accepted=False
    ).exists()

    if existing_exchange:
        # Redirigir o mostrar un mensaje de error si ya existe un intercambio pendiente
        return render(request, 'request_exchange.html', {
            'book': book,
            'form': None,
            'error': 'Ja has enviat una sol·licitud d\'intercanvi per aquest llibre'
        })
    
    if request.method == 'POST':
        form = ExchangeForm(request.POST, user=request.user)
        if form.is_valid():
            exchange = form.save(commit=False)
            exchange.book_for = book
            exchange.book_from = form.cleaned_data['book_to_exchange']
            exchange.from_user = request.user
            exchange.to_user = book.owner
            exchange.save()

            user = book.owner
            user_from = request.user
            title = f"Sol·licitud d'intercanvi per {book.title}"
            message = f"{request.user.first_name} vol intercanviar {exchange.book_from.title} pel teu llibre {book.title}"

            send_user_notification(user, user_from, title, message, exchange)
            
            return redirect('book_details', book_id=book.pk)
    else:
        form = ExchangeForm(user=request.user)
    
    user_books = Book.objects.filter(owner=request.user)

    return render(request, 'request_exchange.html', {
        'book': book,
        'form': form,
        'user_books': user_books,
    })


@login_required
def accept_exchange(request, exchange_id):
    exchange = get_object_or_404(Exchange, pk=exchange_id, to_user=request.user)
    exchange.accepted = True
    exchange.completed = True
    exchange.save()

    # Transferir la propiedad de los libros
    exchange.book_from.owner = exchange.to_user
    exchange.book_for.owner = exchange.from_user
    exchange.book_from.save()
    exchange.book_for.save()

    # Incrementar el contador de intercambios solo si el intercambio es aceptado
    exchange.book_from.exchange_count += 1
    exchange.book_for.exchange_count += 1
    exchange.book_from.save()
    exchange.book_for.save()

    # Enviar notificación al usuario que solicitó el intercambio
    user = exchange.from_user
    user_from = request.user
    title = f"Intercanvi acceptat de {exchange.book_for.title}"
    message = f"{request.user.username} ha acceptat intercanvi {exchange.book_from.title} per {exchange.book_for.title}"
    
    send_user_notification(user, user_from, title, message, None)

    return redirect('notifications')

@login_required
def decline_exchange(request, exchange_id):
    exchange = get_object_or_404(Exchange, pk=exchange_id, to_user=request.user)
    exchange.declined = True
    exchange.completed = True
    exchange.save()

    user = exchange.from_user
    user_from = request.user
    title = f"Intercanvi declinat de {exchange.book_for.title}"
    message = f"{request.user.username} no vol intercanviar {exchange.book_from.title} per {exchange.book_for.title}"

    send_user_notification(user, user_from, title, message, None)

    return redirect('notifications')

@login_required
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id, owner=request.user)

    if request.method == "POST":
        book.delete()
        messages.success(request, f"El llibre '{book.title}' s'ha eliminat correctament.")
        return redirect('dashboard')

    return redirect('dashboard')

@login_required
def add_review_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    
    existing_review = book.book_reviews_recieved.filter(reviewer_id=request.user).first()

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        
        if existing_review:
            # Actualiza la reseña existente
            existing_review.rating = rating
            existing_review.comment = comment
            existing_review.save()
            
        else:
            # Crea una nueva reseña
            book.book_reviews_recieved.create(reviewer_id=request.user.id, rating=rating, comment=comment)
            
        
        return redirect('book_details', book_id=book.pk)
    

    return render(request, 'add_review_book.html', {
        'book': book, 
        'existing_review': existing_review})


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, reviewer=request.user)

    if request.method == "POST":
        review.delete()
        messages.success(request, "La valoració s'ha eliminat correctament.")
        return redirect('book_details', book_id=review.book.id)

    return redirect('book_details', book_id=review.book.id)




