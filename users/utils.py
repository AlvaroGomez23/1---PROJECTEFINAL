from .models import Notification
from django.conf import settings
from django.core.mail import EmailMessage

def send_user_notification(user, user_from, title, message, exchange):
    Notification.objects.create(user=user, user_from=user_from, title=title, message=message, exchange=exchange)

def send_user_email(user, title, message):
    # Construir el mensaje con un enlace clicable
    html_message = f"""
    <p>{message}</p>
    <p>Pots accedir a la pàgina web fent clic al següent enllaç:</p>
    <a href="https://one-projectefinal.onrender.com" target="_blank">https://one-projectefinal.onrender.com</a>
    """

    # Enviar el correo como HTML
    email = EmailMessage(
        subject=title,
        body=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    email.content_subtype = "html" 
    email.send(fail_silently=False)

