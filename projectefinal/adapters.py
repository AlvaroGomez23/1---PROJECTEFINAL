from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from users.models import UserProfile
from django.http import HttpResponseRedirect
User = get_user_model()

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        email = sociallogin.account.extra_data.get('email')

        if not email:
            return  # Sin email, no podemos validar nada

        # Si el sociallogin ya está vinculado (is_existing), no hagas nada
        if sociallogin.is_existing:
            return

        try:
            existing_user = User.objects.get(email=email)

            # Si ya hay un usuario con ese email, pero aún no está vinculado con esta cuenta social
            if not sociallogin.user.pk:
                messages.error(
                    request,
                    "Aquest correu electrònic ja està registrat amb un altre mètode. Intenta iniciar sessió d'una altra manera."
                )
                raise ImmediateHttpResponse(redirect('/users/login'))

        except User.DoesNotExist:
            pass  # No hay conflicto, sigue el flujo normal


    def is_auto_signup_allowed(self, request, sociallogin):
        if request.path == '/accounts/3rdparty/signup/':
            raise ImmediateHttpResponse(redirect('/users/login'))

        return True

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)

        
        email = sociallogin.account.extra_data.get('email') or data.get('email') or ''
        user.username = email
        user.email = email 

        return user
    
    def save_user(self, request, sociallogin, form=None):

        user = super().save_user(request, sociallogin, form)

        UserProfile.objects.get_or_create(user=user)

        return user


class CustomAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return True

    def clean_username(self, username):
        return username 
    
    def get_login_redirect_url(self, request):
        return '/core/dashboard'
    
    def get_connect_redirect_url(self, request, socialaccount):
        return '/core/dashboard'