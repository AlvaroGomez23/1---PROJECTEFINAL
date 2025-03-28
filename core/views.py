from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from books.models import Book, Exchange
from users.models import Notification
from django.db.models import Q, Count

# Create your views here.


def index(request):
    return render(request, 'index.html')

@login_required
def dashboard(request):
    books = Book.objects.filter(owner=request.user)
    last_exchanges = Exchange.objects.filter(accepted=True).order_by('-exchanged_at')[:10]
    
    has_unread_notifications = Notification.objects.filter(user=request.user, is_read=False).exists()

    ranking = (
        Book.objects.filter(
            Q(exchanges_given__completed=True) | Q(exchanges_received__completed=True)
        )
        .values('isbn', 'title', 'author')
        .annotate(
            exchange_count=Count('exchanges_given', distinct=True) + Count('exchanges_received', distinct=True)
        )
        .order_by('-exchange_count')[:10]
    )


    print(books)
    return render(request, 'user.dashboard.html', {
        'books': books,
        'last_exchanges': last_exchanges,
        'has_unread_notifications': has_unread_notifications,
        'ranking': ranking,
    })