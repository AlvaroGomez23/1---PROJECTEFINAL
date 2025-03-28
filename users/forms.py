from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

class Login(forms.Form):
    email = forms.CharField(label="Correu", max_length=100)
    password = forms.CharField(label="Contrasenya", max_length=100, widget=forms.PasswordInput)
    

class Register(forms.Form):
    name = forms.CharField(label="Nom", max_length=100)
    email = forms.CharField(label="Correu", max_length=100)
    password = forms.CharField(label="Contrasenya", max_length=100, widget=forms.PasswordInput)
    password2 = forms.CharField(label="Repeteix contrasenya", max_length=100, widget=forms.PasswordInput)


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']
        labels = {
            'first_name': 'Nom',
            'last_name': 'Cognom',
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['city', 'phone_number']
        labels = {
            'city': 'Ciutat (Pot trigar en carregar degut a la gran quantitat de ciutats)',
            'phone_number': 'Número de telèfon',
        }


class EditProfile(forms.Form):
    first_name = forms.CharField(label="Nom", max_length=100)
    last_name = forms.CharField(label="Cognom", max_length=100)
    city = forms.CharField(label="Ciutat (Pot trigar en carregar degut a la gran quantitat de ciutats)", max_length=100)
    phone_number = forms.CharField(label="Número de telèfon", max_length=100)
