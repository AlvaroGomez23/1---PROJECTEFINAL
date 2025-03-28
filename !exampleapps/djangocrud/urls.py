from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('tasks/', views.tasks, name='tasks'),
    path('logout/', views.logout, name='logout'),
    path('login/', views.login, name='login'),
    path('create_task/', views.create_task, name='create_task'),
    path('task_detail/<int:task_id>/', views.task_detail, name='task_detail'),
]