from django.contrib.auth.models import User
from django.db import models
from books.models import Book
from cities_light.models import City
from books.models import Exchange

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

    def __str__(self):
        return f"Perfil de {self.user.username}"

class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')
    messages = models.TextField(default="", blank=True)  # Mantener el nombre 'messages'
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.id} between {', '.join([user.username for user in self.participants.all()])}"

