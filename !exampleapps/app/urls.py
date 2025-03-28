from django.urls import path
from . import views



urlpatterns = [
    path('', views.index),
    path('hola/<str:username>', views.hola),
    path('pingaso/', views.pingaso),
    path('projects/', views.projects),
    path('tasks/', views.tasks),
    path('form/', views.form1),
]