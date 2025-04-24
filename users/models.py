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

    def __str__(self):
        return f"Perfil de {self.user.username}"

    def average_rating(self):
        reviews = self.user.reviews_received.all()
        if reviews.exists():
            return round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 2)
        return 0

class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')
    messages = models.TextField(default="", blank=True)  # Almacenar mensajes como texto plano
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.id} between {', '.join([user.username for user in self.participants.all()])}"

    def add_message(self, sender, content):
        """Agrega un mensaje a la conversación."""
        new_message = f"{sender.id}|False|{timezone.now().isoformat()}|{content}"
        if self.messages:
            self.messages += f"\n{new_message}"
        else:
            self.messages = new_message
        self.save()

    def get_messages(self):
        """Obtiene todos los mensajes de la conversación como una lista de diccionarios."""
        messages = []
        if self.messages:
            for line in self.messages.split("\n"):
                parts = line.split("|", 3)  # Dividir en 4 partes: sender_id, is_read, timestamp, content
                if len(parts) == 4:
                    messages.append({
                        "sender_id": int(parts[0]),
                        "is_read": parts[1] == "True",
                        "timestamp": parts[2],
                        "content": parts[3],
                    })
        return messages

    def mark_messages_as_read(self, user):
        """Marca los mensajes como leídos para un usuario."""
        updated_messages = []
        if self.messages:
            for line in self.messages.split("\n"):
                parts = line.split("|", 3)
                if len(parts) == 4:
                    if parts[0] != str(user.id):  # Si el mensaje no fue enviado por el usuario actual
                        parts[1] = "True"  # Marcar como leído
                    updated_messages.append("|".join(parts))
            self.messages = "\n".join(updated_messages)
            self.save()

    def count_unread_messages(self, user):
        """Cuenta los mensajes no leídos para un usuario."""
        unread_count = 0
        if self.messages:
            for line in self.messages.split("\n"):
                parts = line.split("|", 3)
                if len(parts) == 4 and parts[0] != str(user.id) and parts[1] == "False":
                    unread_count += 1
        return unread_count
    

class Review(models.Model):
    reviewed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_reviews_received")
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_reviews_given")
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reviewer.username} -> {self.reviewed_user.username} - {self.rating}★"

