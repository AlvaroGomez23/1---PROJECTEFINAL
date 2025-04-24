from django.contrib import admin
from .models import Wishlist, Notification, UserProfile, Review

# Register your models here.

class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user',)  # Muestra el usuario de la wishlist
    filter_horizontal = ('books',)  # Habilita una interfaz amigable para la relación ManyToMany


admin.site.register(Wishlist, WishlistAdmin)
admin.site.register(Notification)
admin.site.register(UserProfile)
admin.site.register(Review)
