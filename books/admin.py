from django.contrib import admin
from .models import Book, Category, Review, Exchange, State

# Register your models here.

admin.site.register(Book)
admin.site.register(Category)
admin.site.register(Review)
admin.site.register(Exchange)
admin.site.register(State)
