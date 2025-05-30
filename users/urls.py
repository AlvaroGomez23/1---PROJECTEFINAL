from django.urls import path
from . import views
from .consumers import ChatConsumer


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
    path('chat/<int:conversation_id>/', views.chat_room, name='chat_room'), 
    path('start_chat/<int:user_id>/', views.private_chat, name='private_chat'),
    path('ws/chat/<int:conversation_id>/', ChatConsumer.as_asgi(), name='chat_ws'),
    path('inbox/', views.inbox, name='inbox'),
    path('mymap/', views.view_map, name='mymap'),
    path('mymap/<int:user_id>/', views.view_map, name='user_map'),
    path('city-autocomplete/', views.city_autocomplete, name='city_autocomplete'),
    path('add_review_user/<int:user_id>', views.add_review_user, name='add_review_user'),
    path('delete_review_user/<int:review_id>', views.delete_review_user, name='delete_review_user'),
    path('recovery_password/', views.recovery_password, name='recovery_password'),
    path('change_recovery_password/<str:token>/', views.change_recovery_password, name='change_recovery_password'),
]