from django import forms
from .models import Project


class createProject(forms.ModelForm):
    title = forms.CharField(label="Titulo", max_length=100)

    