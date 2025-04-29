from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User

class Book(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='books/covers/', null=True, blank=True)
    description = models.TextField()
    author = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    isbn = models.CharField(max_length=13, unique=False)
    state = models.ForeignKey('state', on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="books")
    visible = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now) 
    exchange_count = models.PositiveIntegerField(default=0)  # Contador de intercambios

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.previous_visible = self.visible  # Almacenar el valor inicial de 'visible'

    def save(self, *args, **kwargs):
        # Actualizar el valor previo de 'visible' antes de guardar
        if self.pk:  # Solo si el objeto ya existe en la base de datos
            old_instance = Book.objects.get(pk=self.pk)
            self.previous_visible = old_instance.visible
        super().save(*args, **kwargs)

    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 2)
        return 0

    def __str__(self):
        return self.title



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
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1 a 5 estrellas
    comment = models.TextField(blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reviewer.username} - {self.rating}★"



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
