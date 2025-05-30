from django.contrib.auth.models import User
from django.db import models
from books.models import Book
from cities_light.models import City
from books.models import Exchange
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.db.models import Avg

class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wishlist")
    books = models.ManyToManyField(Book, blank=True)
    desired_isbns = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Wishlist de {self.user.username}"
    
    
    @classmethod
    def get_wishlists_with_isbn(cls, isbn):
        return cls.objects.filter(desired_isbns__icontains=isbn)
    
    @classmethod
    def get_or_create_for_user(cls, user):
        wishlist, created = cls.objects.get_or_create(user=user)
        return wishlist

    def add_isbn(self, isbn):
        if not isbn:
            return
        isbns = self.get_isbns()
        if isbn not in isbns:
            isbns.append(isbn)
            self.desired_isbns = ','.join(isbns)
            self.save()

    def remove_isbn(self, isbn):
        if not isbn:
            return
        isbns = self.get_isbns()
        if isbn in isbns:
            isbns.remove(isbn)
            self.desired_isbns = ','.join(isbns) if isbns else None
            self.save()

    def get_isbns(self):
        return self.desired_isbns.split(',') if self.desired_isbns else []

    def get_books(self, search_query=None):
        qs = self.books.all()
        if search_query:
            qs = qs.filter(title__icontains=search_query) | qs.filter(isbn__icontains=search_query)
        return qs

    def toggle_book(self, book):
        if book in self.books.all():
            self.books.remove(book)
            self.remove_isbn(book.isbn)
            return 'removed'
        else:
            self.books.add(book)
            self.add_isbn(book.isbn)
            return 'added'

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
    
    @classmethod
    def get_noti_user(cls, user):
        return cls.objects.filter(user=user).select_related('exchange').order_by('-created_at')
    
    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    phone_number = models.CharField(max_length=11, blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    movement_radius_km = models.PositiveIntegerField(default=3)
    veto = models.BooleanField(default=False)
    recovery_token = models.UUIDField(null=True, blank=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"

    def average_rating(self):
        reviews = self.user.reviews_received.all()
        if reviews.exists():
            return round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 2)

    def update_from_form(self, form):
        for field, value in form.cleaned_data.items():
            setattr(self, field, value)

        if self.city:
            self.latitude = self.city.latitude
            self.longitude = self.city.longitude

        self.save()

    @staticmethod
    def email_exists(email):
        return User.objects.filter(email=email).exists()
    
    def get_user(email):
        return User.objects.filter(email=email).first()
    
    @classmethod
    def get_user_profile_by_email(cls, email):
        return cls.objects.filter(user__email=email).first()
    
    @classmethod
    def register_allauth_user(cls, user):
        cls.objects.create(user=user)

    @classmethod
    def register_user(cls, name, email, password, password2):
        if password != password2:
            raise ValueError("Les contrasenyes no coincideixen")

        try:
            validate_password(password)
        except ValidationError as e:
            raise ValueError(e.messages[0])

        if cls.email_exists(email):
            raise ValueError("Aquest correu electr\ònic ja est\à registrat")

        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = name
        user.save()

        cls.objects.create(user=user)
        return user

    @classmethod
    def obtain_user(cls, user_id, request_user):
        user = request_user if user_id is None or user_id == request_user.id else get_object_or_404(User, pk=user_id)

        profile = cls.objects.filter(user=user).first()
        reviews = user.user_reviews_received.all()
        avg_rating = round(reviews.aggregate(Avg('rating'))['rating__avg'] or 0, 2)
        veto = profile.veto if profile else False

        return {
            'user': user,
            'profile_info': profile,
            'reviews': reviews,
            'average_rating': avg_rating,
            'veto': veto,
            'other_user': user
        }

    def get_map_context(self):
        return {
            'lat': self.latitude,
            'lng': self.longitude,
            'radius': self.movement_radius_km,
            'user': self.user,
        }
    
    @classmethod
    def get_by_user(cls, user):
        return cls.objects.filter(user=user).first()

    @classmethod
    def get_profile_for_map(cls, user_id=None, current_user=None):
        data = cls.obtain_user(user_id, current_user)
        return data.get('profile_info')
    
    def save_token(self, token):
        self.recovery_token = token
        self.save()


    @classmethod
    def get_by_token(cls, token):
        return cls.objects.filter(recovery_token=token).first()

    def change_password(self, new_password):
        self.user.set_password(new_password)
        self.recovery_token = None 
        self.user.save()
        self.save()

class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')
    messages = models.TextField(default="", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.id} between {', '.join([user.username for user in self.participants.all()])}"

    def has_participant(self, user):
        return self.participants.filter(id=user.id).exists()

    def get_other_participant(self, user):
        return self.participants.exclude(id=user.id).first()

    def get_info_for_user(self, user):

        other = self.get_other_participant(user)
        return {
            "conversation": self,
            "other_user_id": other.id if other else None,
            "other_user_name": other.first_name if other else "Desconegut",
        }

    @classmethod
    def get_conversations_for_user(cls, user):
        
        conversations = cls.objects.filter(participants=user)
        return [conv.get_info_for_user(user) for conv in conversations]

    @classmethod
    def get_or_create_between_users(cls, user1, user2):
        conversation = cls.objects.filter(participants=user1).filter(participants=user2).first()
        if conversation:
            return conversation, False

        conversation = cls.objects.create()
        conversation.participants.add(user1, user2)
        return conversation, True

    

class Review(models.Model):
    reviewed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_reviews_received")
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_reviews_given")
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reviewer.username} -> {self.reviewed_user.username} - {self.rating}★"
    
    @classmethod
    def get_review(cls, reviewer, reviewed_user):
        return cls.objects.filter(reviewer=reviewer, reviewed_user=reviewed_user).first()

    @classmethod
    def add_or_update_review(cls, reviewer, reviewed_user, rating, comment):
        review, created = cls.objects.get_or_create(
            reviewer=reviewer,
            reviewed_user=reviewed_user,
            defaults={'rating': rating, 'comment': comment}
        )
        if not created:
            review.rating = rating
            review.comment = comment
            review.save()
        return review, created
    
    @classmethod
    def delete_review(cls, review_id, reviewer):
        review = cls.objects.filter(id=review_id, reviewer=reviewer).first()
        if review:
            reviewed_user_id = review.reviewed_user.id
            review.delete()
            return True, reviewed_user_id
        return False, None

