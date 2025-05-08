from django.contrib.auth.models import User
from django.db import models
from books.models import Book
from cities_light.models import City
from books.models import Exchange
import json
from django.utils import timezone

class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wishlist")
    books = models.ManyToManyField(Book, blank=True)
    desired_isbns = models.TextField(blank=True, null=True)  # Lista de ISBNs separados por comas

    def __str__(self):
        return f"Wishlist de {self.user.username}"

    def add_isbn(self, isbn):
        """Agrega un ISBN a la lista de deseados."""
        if not isbn:
            return
        isbns = self.get_isbns()
        if isbn not in isbns:
            isbns.append(isbn)
            self.desired_isbns = ','.join(isbns)
            self.save()

    def get_isbns(self):
        """Devuelve la lista de ISBN deseados."""
        return self.desired_isbns.split(',') if self.desired_isbns else []

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    user_from = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications_from", null=True, blank=True)
    exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE, related_name="notifications", null=True, blank=True)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notificación para {self.user.username}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    movement_radius_km = models.PositiveIntegerField(default=3)
    veto = models.BooleanField(default=False)

    def __str__(self):
        return f"Perfil de {self.user.username}"

    def average_rating(self):
        reviews = self.user.reviews_received.all()
        if reviews.exists():
            return round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 2)
        return 0

class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')
    messages = models.TextField(default="", blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.id} between {', '.join([user.username for user in self.participants.all()])}"

    

class Review(models.Model):
    reviewed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_reviews_received")
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_reviews_given")
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reviewer.username} -> {self.reviewed_user.username} - {self.rating}★"

