from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from users.models import UserProfile

User = get_user_model()

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        Si un usuario intenta iniciar sesión con una cuenta social cuyo email ya está
        registrado en el sistema, y no está enlazado, rechazamos el intento.
        """
        email = sociallogin.account.extra_data.get('email')

        if email:
            try:
                existing_user = User.objects.get(email=email)

                if not sociallogin.is_existing:
                    messages.error(
                        request,
                        "Aquest correu electrònic ja està registrat. Si no t'enrecordes de la contrasenya, prova a restablir-la."
                    )
                    raise ImmediateHttpResponse(redirect('/users/login'))

            except User.DoesNotExist:
                pass

    def is_auto_signup_allowed(self, request, sociallogin):
        return True  # Permitimos el auto-signup solo si no se ha bloqueado antes

    def populate_user(self, request, sociallogin, data):
        """
        Este método se llama al crear el usuario. Usamos el `first_name` como username.
        """
        user = super().populate_user(request, sociallogin, data)
        email = sociallogin.account.extra_data.get('email')
        user.username = email
        return user
    
    def save_user(self, request, sociallogin, form=None):
        """
        Este método guarda el usuario y luego crea el UserProfile.
        """
        user = super().save_user(request, sociallogin, form)

        # Crear el perfil si no existe
        UserProfile.objects.get_or_create(user=user)

        return user


class CustomAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        """
        Controla si se permite el signup local (opcional).
        """
        return True

    def clean_username(self, username):
        """
        Si `ACCOUNT_USERNAME_REQUIRED = False`, esto puede quedar vacío o pasarse por alto.
        """
        return username  # No validamos unicidad si no es necesario
