from django.contrib import admin
from .models import Wishlist, Notification, UserProfile, Review, Conversation

# Register your models here.

class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user',)
    filter_horizontal = ('books',)


admin.site.register(Wishlist, WishlistAdmin)
admin.site.register(Notification)
admin.site.register(UserProfile)
admin.site.register(Review)
admin.site.register(Conversation)
