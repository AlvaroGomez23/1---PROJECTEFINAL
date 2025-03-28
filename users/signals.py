from django.db.models.signals import post_save
from django.dispatch import receiver
from books.models import Book
from .models import Wishlist, Notification

@receiver(post_save, sender=Book)
def notify_users_on_new_book(sender, instance, created, **kwargs):
    if created:  # Solo actuar cuando se crea un nuevo libro
        isbn = instance.isbn
        wishlists = Wishlist.objects.filter(desired_isbns__icontains=isbn)  # Buscar listas que contengan el ISBN
        for wishlist in wishlists:
            user = wishlist.user
            if instance.visible:  # Verificar si el libro es visible
                Notification.objects.create(
                    user=user,
                    user_from=None,  # Opcional: puedes dejarlo vacío o asignar un usuario específico
                    title="Nou llibre disponible!",
                    message=f"El llibre amb ISBN {isbn} que desitjaves ja està disponible: {instance.title}",
                )
            else:  # Si el libro no es visible
                Notification.objects.create(
                    user=user,
                    user_from=None,
                    title="Nou llibre afegit (no visible)",
                    message=f"El llibre amb ISBN {isbn} que desitjaves ha estat afegit, però encara no està visible. {instance.title}. Et recomanem que revisis més tard.",
                )



@receiver(post_save, sender=Book)
def notify_users_on_book_visibility_change(sender, instance, created, **kwargs):
    if not created:  # Solo actuar cuando se actualiza un libro existente
        # Verificar si el libro se ha hecho visible
        if instance.visible and instance.previous_visible is False:  # Si antes no era visible y ahora sí
            isbn = instance.isbn
            wishlists = Wishlist.objects.filter(desired_isbns__icontains=isbn)  # Buscar listas que contengan el ISBN
            for wishlist in wishlists:
                user = wishlist.user
                Notification.objects.create(
                    user=user,
                    user_from=None,
                    title="Nou llibre disponible!",
                    message=f"El llibre amb ISBN {isbn} que desitjaves ja està disponible: {instance.title}",
                )