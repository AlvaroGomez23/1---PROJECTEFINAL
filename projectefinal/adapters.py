from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_auto_signup_allowed(self, request, sociallogin):
        email = sociallogin.account.extra_data.get('email')
        if email and User.objects.filter(email=email).exists():
            messages.error(request, "Aquest correu electrònic ja està registrat. Si no t'enrecordes de la contrasenya, prova a restablir-la.")
            raise ImmediateHttpResponse(redirect('/users/login'))  # Redirige al login
        return super().is_auto_signup_allowed(request, sociallogin)
