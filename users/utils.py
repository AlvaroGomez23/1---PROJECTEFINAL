from .models import Notification
from django.conf import settings
from django.core.mail import send_mail

def send_user_notification(user, user_from, title, message, exchange):
    Notification.objects.create(user=user, user_from=user_from, title=title, message=message, exchange=exchange)

def send_user_email(user, title, message,):

    
    send_mail(
        subject=title,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
   
