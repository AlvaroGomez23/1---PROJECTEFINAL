from django import forms
from .models import Category, Book, Exchange

class createBook(forms.ModelForm):
    image = forms.ImageField(required=False, label='Imatge')
    price = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        label='Preu',
        max_value=200,
        min_value=0,
        widget=forms.NumberInput(attrs={'max': 200, 'min': 0, 'step': '0.01'})
    )
    isbn = forms.CharField(
        label='ISBN',
        min_length=13,
        max_length=13,
        widget=forms.TextInput(attrs={'title': 'Introdueix 13 dígits numèrics'}),
        help_text='Introdueix 13 dígits numèrics'
    )

    class Meta:
        model = Book
        fields = ['title', 'author', 'category', 'description', 'price', 'isbn', 'state', 'visible']
        labels = {
            'title': 'Títol',
            'author': 'Autor',
            'category': 'Categoria',
            'description': 'Descripció',
            'price': 'Preu',
            'isbn': 'ISBN',
            'state': 'Estat',
            'visible': 'Visible'
        }

    category = forms.ModelChoiceField(queryset=Category.objects.all(), label="Categoria")

    def clean_isbn(self):
        isbn = self.cleaned_data['isbn']
        if not isbn.isdigit():
            raise forms.ValidationError("L'ISBN ha de contenir només números.")
        if len(isbn) != 13:
            raise forms.ValidationError("L'ISBN ha de tenir exactament 13 dígits.")
        return isbn



class ExchangeForm(forms.ModelForm):
    book_to_exchange = forms.ModelChoiceField(queryset=Book.objects.none())

    class Meta:
        model = Exchange
        fields = ['book_to_exchange']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ExchangeForm, self).__init__(*args, **kwargs) # Crida al constructor de la classe pare
        if user:
            self.fields['book_to_exchange'].queryset = Book.objects.filter(owner=user) # Omplena el desplegable amb els llibres de l'usuari