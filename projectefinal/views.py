from django.shortcuts import redirect
from django.contrib import messages

def redirect_signup_to_login_with_message(request):
    messages.error(request, "Ja existeix un compte amb aquest correu. Prova amb google o restableix la contrasenya.")
    return redirect('/users/login')