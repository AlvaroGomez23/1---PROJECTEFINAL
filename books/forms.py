from django import forms
from .models import Category, Book, Exchange

class createBook(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'category', 'description','price', 'isbn', 'state', 'link', 'image', 'visible']
        labels = {
            'title': 'Títol',
            'author': 'Autor',
            'category': 'Categoria',
            'description': 'Descripció',
            'price': 'Preu',
            'isbn': 'ISBN',
            'state': 'Estat',
            'link': 'Enllaç',
            'image': 'Imatge',
            'visible': 'Visible'
        }

    category = forms.ModelChoiceField(queryset=Category.objects.all(), label="Categoria")



class ExchangeForm(forms.ModelForm):
    book_to_exchange = forms.ModelChoiceField(queryset=Book.objects.none(), label="Libro para intercambiar")

    class Meta:
        model = Exchange
        fields = ['book_to_exchange']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ExchangeForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['book_to_exchange'].queryset = Book.objects.filter(owner=user)