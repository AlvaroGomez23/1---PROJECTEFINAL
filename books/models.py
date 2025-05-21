from django.utils import timezone
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

class Book(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='books/covers', null=True, blank=True)
    description = models.TextField()
    author = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    isbn = models.CharField(max_length=13, unique=False)
    state = models.ForeignKey('state', on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="books")
    visible = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    exchange_count = models.PositiveIntegerField(default=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.previous_visible = self.visible

    def save(self, *args, **kwargs):
        if self.pk:
            old_instance = Book.objects.get(pk=self.pk)
            self.previous_visible = old_instance.visible
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 2)
        return 0

    def is_exchangeable_by(self, user):
        """Verifica si el usuario puede solicitar un intercambio por este libro"""
        if user.userprofile.veto:
            return False, "Has sigut vetat degut a un comportament inadequat. No pots intercanviar llibres."
        if self.owner.userprofile.veto:
            return False, "El propietari del llibre ha sigut vetat degut a un comportament inadequat."
        if self.owner == user:
            return False, "No pots intercanviar llibres amb tu mateix."
        return True, None

    def has_pending_exchange_with(self, user):
        """Comprueba si ya existe un intercambio pendiente con este libro"""
        return Exchange.objects.filter(
            book_for=self,
            book_from__in=Book.objects.filter(owner=user),
            from_user=user,
            to_user=self.owner,
            completed=False,
            declined=False,
            accepted=False
        ).exists()

    @classmethod
    def create_book(cls, form, user):
        """Crea un libro a partir de un formulario y usuario"""
        book = form.save(commit=False)
        book.owner = user
        book.save()
        return book

    @classmethod
    def update_book(cls, form):
        """Actualiza un libro desde un formulario ya vinculado a la instancia"""
        updated_book = form.save(commit=False)
        updated_book.save()
        return updated_book

    @classmethod
    def get_book(cls, book_id):
        return get_object_or_404(cls, id=book_id)

    @classmethod
    def get_9_books(cls):
        return cls.objects.filter(visible=True).order_by('-created_at')[:9]

    @classmethod
    def get_visible_books_for_user(cls, user):
        return cls.objects.filter(visible=True).exclude(owner=user)

    @classmethod
    def filter_books(cls, books, params):
        """Aplica filtros dinámicos según los parámetros recibidos"""
        title_or_isbn = params.get('title', '')
        author = params.get('author', '')
        min_price = params.get('min_price')
        max_price = params.get('max_price')
        category = params.get('category', '')

        if title_or_isbn:
            books = books.filter(Q(title__icontains=title_or_isbn) | Q(isbn__icontains=title_or_isbn))
        if author:
            books = books.filter(author__icontains=author)
        if min_price:
            books = books.filter(price__gte=min_price)
        if max_price:
            books = books.filter(price__lte=max_price)
        if category:
            books = books.filter(category__name=category)

        return books

    @classmethod
    def get_exchanges_pending_map(cls, books, user):
        """Devuelve un diccionario que indica si cada libro tiene un intercambio pendiente para el usuario"""
        return {
            book.id: Exchange.objects.filter(
                book_for=book,
                from_user=user,
                completed=False,
                declined=False
            ).exists()
            for book in books
        }
    
    def delete_book(self):
        if self.image:
            self.image.delete(save=False)
        self.delete()



class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
class State(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=True, blank=True, related_name="book_reviews_recieved")
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="book_reviews_given")
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reviewer.username} - {self.rating}★"

    @classmethod
    def get_review(cls, review_id):
        return get_object_or_404(cls, id=review_id)

    @classmethod
    def get_existing_review(cls, book, reviewer):
        return cls.objects.filter(book=book, reviewer=reviewer).first()

    @classmethod
    def create_review(cls, book, reviewer, rating, comment):
        return cls.objects.create(book=book, reviewer=reviewer, rating=rating, comment=comment)

    @classmethod
    def delete_review(cls, review_id, reviewer):
        review = cls.objects.filter(id=review_id, reviewer=reviewer).first()
        if review:
            book_id = review.book.id
            review.delete()
            return True, book_id
        return False, None

    def update_review(self, rating, comment):
        self.rating = rating
        self.comment = comment
        self.save()



class Exchange(models.Model):
    book_from = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="exchanges_given")
    book_for = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="exchanges_received")
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="exchanges_given")
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="exchanges_received")
    completed = models.BooleanField(default=False)
    accepted = models.BooleanField(default=False)
    declined = models.BooleanField(default=False)
    exchanged_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.book_from.title} <--- {self.from_user.username} ------- {self.to_user.username} ---> {self.book_for.title}"

    @classmethod
    def get_exchange(cls, exchange_id):
        return get_object_or_404(cls, id=exchange_id)
    
    @classmethod
    def create_exchange(cls, book_for, book_from, from_user, to_user):
        exchange = cls(
            book_for=book_for,
            book_from=book_from,
            from_user=from_user,
            to_user=to_user
        )
        exchange.save()
        return exchange

    def perform_accept_exchange(self, current_user):
        if self.book_for.owner != current_user:
            raise PermissionError("Este usuario no puede aceptar el intercambio.")

        self.accepted = True
        self.completed = True
        self.save()

        # Intercambio de propietarios
        self.book_from.owner = self.to_user
        self.book_for.owner = self.from_user

        self.book_from.exchange_count += 1
        self.book_for.exchange_count += 1

        self.book_from.save()
        self.book_for.save()

    def perform_decline_exchange(self, current_user):
        if self.to_user != current_user:
            raise PermissionError("Este usuario no puede rechazar este intercambio.")

        self.declined = True
        self.completed = True
        self.save()
