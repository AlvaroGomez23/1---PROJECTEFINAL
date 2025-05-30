from django import forms
from django.contrib.auth.models import User
from .models import UserProfile
from cities_light.models import City

class Login(forms.Form):
    email = forms.CharField(label="Correu", max_length=100)
    password = forms.CharField(label="Contrasenya", max_length=100, widget=forms.PasswordInput)
    

class Register(forms.Form):
    name = forms.CharField(label="Nom", max_length=30)
    email = forms.CharField(label="Correu", max_length=100)
    password = forms.CharField(label="Contrasenya", max_length=100, widget=forms.PasswordInput)
    password2 = forms.CharField(label="Repeteix contrasenya", max_length=100, widget=forms.PasswordInput)


class CombinedUserProfileForm(forms.Form):
    # Campos del modelo User
    first_name = forms.CharField(
        label='Nom *',
        max_length=30,
        required=True
    )
    last_name = forms.CharField(
        label='Cognom',
        max_length=50,
        required=False
    )

    # Campos del modelo UserProfile
    city = forms.ModelChoiceField(
        label='Selecciona el teu poble',
        queryset=City.objects.all(),
        widget=forms.HiddenInput(),
        required=False
    )
    phone_number = forms.CharField(
        label='Número de telèfon',
        max_length=11,
        required=False
    )
    movement_radius_km = forms.IntegerField(
        label='Radi de moviment (km) *',
        min_value=1,
        max_value=100,
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name

            profile = getattr(self.user, 'userprofile', None)
            if profile:
                self.fields['city'].initial = profile.city
                self.fields['phone_number'].initial = profile.phone_number
                self.fields['movement_radius_km'].initial = profile.movement_radius_km

    def save(self):
        # Guardar datos del modelo User
        self.user.first_name = self.cleaned_data['first_name']
        self.user.last_name = self.cleaned_data['last_name']
        self.user.save()

        # Guardar datos del modelo UserProfile
        profile = self.user.userprofile
        profile.phone_number = self.cleaned_data['phone_number']
        profile.movement_radius_km = self.cleaned_data['movement_radius_km']
        profile.city = self.cleaned_data['city']

        if profile.city:
            profile.latitude = profile.city.latitude
            profile.longitude = profile.city.longitude

        profile.save()

        return self.user

class EditProfile(forms.Form):
    first_name = forms.CharField(label="Nom", max_length=100)
    last_name = forms.CharField(label="Cognom", max_length=100)
    city = forms.CharField(label="Ciutat (Pot trigar en carregar degut a la gran quantitat de ciutats)", max_length=100)
    phone_number = forms.CharField(label="Número de telèfon", max_length=100)


class RecoveryPassword(forms.Form):
    email = forms.CharField(label="Correu", max_length=100)


class ChangeRecoveryPassword(forms.Form):
    password = forms.CharField(label="Contrasenya", max_length=100, widget=forms.PasswordInput)
    password2 = forms.CharField(label="Repeteix contrasenya", max_length=100, widget=forms.PasswordInput)