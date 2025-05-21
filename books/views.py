from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from .models import Book, Exchange, Category, Review
from users.models import Wishlist, Notification
from .forms import createBook, ExchangeForm
from django.contrib.auth.decorators import login_required
from users.utils import send_user_notification, send_user_email
from django.db.models import Avg
from django.contrib import messages
from django.urls import reverse
from django.core.paginator import Paginator


# Create your views here.


def books(request):
    all_books = Book.get_visible_books_for_user(request.user)
    filtered_books = Book.filter_books(all_books, request.GET)

    paginator = Paginator(filtered_books, 2)  # 9 libros por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    exchanges_pending = Book.get_exchanges_pending_map(page_obj.object_list, request.user)

    context = {
        'books': page_obj.object_list,
        'exchanges_pending': exchanges_pending,
        'user_wishlist': Wishlist.objects.filter(user=request.user).first(),
        'categories': Category.objects.all(),
        'page_obj': page_obj,  # útil para los controles de paginación
    }
    return render(request, 'books.html', context)


def book_details(request, book_id):
    book = Book.get_book(book_id)
    reviews = book.book_reviews_recieved.all()
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    context = {
        'book': book,
        'reviews': reviews,
        'average_rating': average_rating,
    }
    return render(request, 'book_details.html', context)



def check_isbn_in_wishlists(isbn):
    wishlists = Wishlist.get_wishlists_with_isbn(isbn)
    for wishlist in wishlists:
        user = wishlist.user
        title = f"Un llibre desitjat està disponible!"
        message = f"El llibre amb ISBN {isbn} que desitjes, ara està disponible."
        send_user_notification(user, None, title, message, None)
        send_user_email(user, title, message)

    


@login_required
def create_book(request):
    form = createBook(request.POST or None, request.FILES or None)
    
    if request.method == 'POST' and form.is_valid():
        book = Book.create_book(form, request.user)
        return redirect('book_details', book_id=book.pk)

    return render(request, 'create_book.html', {'form': form})
    

@login_required
def modify_book(request, book_id):
    book = Book.get_book(book_id)

    if book.owner != request.user:
        return redirect('books')

    form = createBook(request.POST or None, request.FILES or None, instance=book)

    if request.method == 'POST' and form.is_valid():
        book.update_book(form)
        messages.success(request, f"El llibre '{book.title}' s'ha modificat correctament.")
        return redirect('book_details', book_id=book.pk)

    return render(request, 'modify_book.html', {
        'form': form,
        'book': book
    })
    

def new_books(request):
    books = Book.get_9_books()
    user_wishlist = Wishlist.get_or_create_for_user(user=request.user)
    return render(request, 'new_books.html', {
        'books': books,
        'user_wishlist': user_wishlist,  
    })


@login_required
def request_exchange(request, book_id):
    book = Book.get_book(book_id)
    user = request.user

    # Validación de intercambio
    can_exchange, error_message = book.is_exchangeable_by(user)
    if not can_exchange:
        messages.error(request, error_message)
        return redirect('books')

    if book.has_pending_exchange_with(user):
        return render(request, 'request_exchange.html', {
            'book': book,
            'form': None,
            'error': 'Ja has enviat una sol·licitud d\'intercanvi per aquest llibre'
        })

    if request.method == 'POST':
        form = ExchangeForm(request.POST, user=user)
        if form.is_valid():
            book_to_exchange = form.cleaned_data['book_to_exchange']
            exchange = Exchange.create_exchange(book, book_to_exchange, user, book.owner)

            # Notificació
            title = f"Sol·licitud d'intercanvi per {book.title}"
            url = reverse('book_details', args=[exchange.book_from.id])
            message = f"{user.first_name} vol intercanviar <a href='{url}'>{exchange.book_from.title}</a> pel teu llibre {book.title}"
            send_user_notification(book.owner, user, title, message, exchange)
            send_user_email(book.owner, title, f"{user.first_name} vol intercanviar {exchange.book_from.title} pel teu llibre {book.title}")

            return redirect('book_details', book_id=book.pk)
    else:
        form = ExchangeForm(user=user)

    return render(request, 'request_exchange.html', {
        'book': book,
        'form': form,
        'user_books': Book.objects.filter(owner=user),
    })

@login_required
def accept_exchange(request, exchange_id):
    exchange = Exchange.get_exchange(exchange_id)

    try:
        exchange.perform_accept_exchange(request.user)

        title = f"Intercanvi acceptat de {exchange.book_for.title}"
        message = f"{request.user.username} ha acceptat intercanvi {exchange.book_from.title} per {exchange.book_for.title}"

        send_user_notification(exchange.from_user, request.user, title, message, None)
        send_user_email(exchange.from_user, title, message)

        messages.success(request, "L'intercanvi s'ha efectuat correctament.")

    except PermissionError:
        messages.error(request, "No pots acceptar aquest intercanvi perquè el llibre no està en la teva possessió.")
    
    except Exception:
        messages.error(request, "S'ha produït un error inesperat en acceptar l'intercanvi.")

    return redirect('notifications')

@login_required
def decline_exchange(request, exchange_id):
    exchange = get_object_or_404(Exchange, pk=exchange_id)

    try:
        exchange.perform_decline_exchange(request.user)

        # Notificación
        user = exchange.from_user
        user_from = request.user
        title = f"Intercanvi declinat de {exchange.book_for.title}"
        message = f"{request.user.username} no vol intercanviar {exchange.book_from.title} per {exchange.book_for.title}"

        send_user_notification(user, user_from, title, message, None)
        send_user_email(user, title, message)

        messages.success(request, "Has declinat correctament l'intercanvi.")

    except PermissionError:
        messages.error(request, "No tens permís per declinar aquest intercanvi.")

    except Exception:
        messages.error(request, "S'ha produït un error en declinar l'intercanvi.")

    return redirect('notifications')

@login_required
def delete_book(request, book_id):
    book = Book.get_book(book_id)

    if request.method == "POST":
        book_title = book.title
        book.delete_book()
        messages.success(request, f"El llibre '{book_title}' s'ha eliminat correctament.")
        return redirect('dashboard')

    return redirect('dashboard')

@login_required
def add_review_book(request, book_id):
    book = Book.get_book(book_id)
    user = request.user
    userprofile = user.userprofile

    if userprofile.veto:
        messages.error(request, "Has sigut vetat degut a un comportament inadequat. No pots valorar llibres.")
        return redirect('book_details', book_id=book.pk)

    existing_review = Review.get_existing_review(book, user)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        if existing_review:
            existing_review.update_review(rating, comment)
            messages.success(request, "La valoració s'ha actualitzat correctament.")
        else:
            Review.create_review(book, user, rating, comment)
            messages.success(request, "La valoració s'ha afegit correctament.")

        return redirect('book_details', book_id=book.pk)

    return render(request, 'add_review_book.html', {
        'book': book,
        'existing_review': existing_review
    })


@login_required
def delete_review(request, review_id):
    success, book_id = Review.delete_review(review_id, request.user)

    if success:
        messages.success(request, "La valoració s'ha eliminat correctament.")
    else:
        messages.error(request, "No s'ha pogut eliminar la valoració.")

    return redirect('book_details', book_id=book_id or 0)




