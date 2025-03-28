from django.urls import path
from . import views



urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    path('view_profile/<int:user_id>/', views.view_profile, name='view_profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/mark_as_read/<int:notification_id>/', views.mark_as_read, name='mark_as_read'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('toggle_wishlist/', views.toggle_wishlist, name='toggle_wishlist'),
]