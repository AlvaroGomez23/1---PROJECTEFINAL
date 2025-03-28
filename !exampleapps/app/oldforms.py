from django import forms
from .models import Task

class createTask(forms.ModelForm):
    title = forms.CharField(label="Titulo", max_length=100)
    description = forms.CharField(label="Descripcion", max_length=100, widget=forms.Textarea)

    class Meta:
        model = Task
        fields = ['title', 'description']