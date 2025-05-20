from .models import Notification
from django.conf import settings
from django.core.mail import EmailMessage
from django.contrib import messages
from django.shortcuts import redirect
from cities_light.models import City

def send_user_notification(user, user_from, title, message, exchange):
    Notification.objects.create(user=user, user_from=user_from, title=title, message=message, exchange=exchange)

def send_user_email(user, title, message):
    # Missatge HTML per al correu electrònic
    html_message = f"""
    <p>{message}</p>
    <p>Pots accedir a la pàgina web fent clic al següent enllaç:</p>
    <a href="https://one-projectefinal.onrender.com" target="_blank">https://one-projectefinal.onrender.com</a>
    """

    email = EmailMessage(
        subject=title,
        body=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    email.content_subtype = "html" 
    email.send(fail_silently=False)

def check_veto(request, target_user):
    if request.user.userprofile.veto:
        messages.error(request, "No pots fer valoracions amb el teu perfil actual ja que has sigut vetat.")
        return redirect('books')  # o la ruta que corresponda
    if target_user.userprofile.veto:
        messages.error(request, "Aquest usuari ha estat vetat. No pots valorar-lo.")
        return redirect('books')  # o otra página segura
    return None

def search_cities(term, limit=10):
    return City.objects.filter(name__icontains=term).values('id', 'name')[:limit]

