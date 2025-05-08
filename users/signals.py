from django.db.models.signals import post_save
from django.dispatch import receiver
from books.models import Book
from .models import Wishlist, Notification
from users.utils import send_user_email

@receiver(post_save, sender=Book)
# Envia notificacions i emails als usuaris quan un llibre amb un isbn que tenen a la seva llista de desitjos és afegit o actualitzat.
def notify_users_on_new_book(sender, instance, created, **kwargs):
    if created:  
        isbn = instance.isbn
        wishlists = Wishlist.objects.filter(desired_isbns__icontains=isbn)
        for wishlist in wishlists:
            user = wishlist.user
            if instance.visible:  
                Notification.objects.create(
                    user=user,
                    user_from=None, 
                    title="Nou llibre disponible!",
                    message=f"El llibre amb ISBN {isbn} que desitjaves ja està disponible: {instance.title}",
                )
                send_user_email(
                    user=user,
                    title="Nou llibre disponible!",
                    message=f"El llibre amb ISBN {isbn} que desitjaves ja està disponible: {instance.title}",
                )
            else:  
                Notification.objects.create(
                    user=user,
                    user_from=None,
                    title="Nou llibre afegit (no visible)",
                    message=f"El llibre amb ISBN {isbn} que desitjaves ha estat afegit, però encara no està visible. {instance.title}. Et recomanem que revisis més tard.",
                )
                send_user_email(
                    user=user,
                    title="Nou llibre afegit (no visible)",
                    message=f"El llibre amb ISBN {isbn} que desitjaves ha estat afegit, però encara no està visible. {instance.title}. Et recomanem que revisis més tard.",
                )



@receiver(post_save, sender=Book)
# Envia notificacions i emails als usuaris quan un llibre amb un isbn que tenen a la seva llista de desitjos és actualitzat.
def notify_users_on_book_visibility_change(sender, instance, created, **kwargs):
    if not created: 
        if instance.visible and instance.previous_visible is False:  
            isbn = instance.isbn
            wishlists = Wishlist.objects.filter(desired_isbns__icontains=isbn) 
            for wishlist in wishlists:
                user = wishlist.user
                Notification.objects.create(
                    user=user,
                    user_from=None,
                    title="Nou llibre disponible!",
                    message=f"El llibre amb ISBN {isbn} que desitjaves ja està disponible: {instance.title}",
                )
                send_user_email(
                    user=user,
                    title="Nou llibre disponible!",
                    message=f"El llibre amb ISBN {isbn} que desitjaves ja està disponible: {instance.title}",
                )