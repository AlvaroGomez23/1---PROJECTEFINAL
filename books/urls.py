from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views



urlpatterns = [
   path('', views.books, name='books'),
   path('book_details/<int:book_id>', views.book_details, name='book_details'),
   path('create_book/', views.create_book, name='create_book'),
   path('modify_book/<int:book_id>', views.modify_book, name='modify_book'),
   path('new_books/', views.new_books, name='new_books'),
   path('request_exchange/<int:book_id>', views.request_exchange, name='request_exchange'),
   path('accept_exchange/<int:exchange_id>/', views.accept_exchange, name='accept_exchange'),
   path('decline_exchange/<int:exchange_id>/', views.decline_exchange, name='decline_exchange'),
   path('delete_book/<int:book_id>/', views.delete_book, name='delete_book'),
   path('add_review_book/<int:book_id>/', views.add_review_book, name='add_review_book'),
   path('delete_review/<int:review_id>/', views.delete_review, name='delete_review'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

