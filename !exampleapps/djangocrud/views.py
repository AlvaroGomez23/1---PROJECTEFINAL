from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as l_login, logout as d_logout, authenticate
from django.contrib.auth.models import User
from django.http import HttpResponse
from .forms import TaskForm
from django.contrib.auth.decorators import login_required
from .models import Task

# Create your views here.

def home(request):
    return render(request, 'hmp.html')

def signup(request):

    if request.method == 'GET':
        form = UserCreationForm()
        return render(request, 'signup.html', {'form': form})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.get(username=request.POST['username'])
                return render(request, 'signup.html', {'errors': 'Usuario ya existe'})
            except User.DoesNotExist:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                l_login(request, user)
                return redirect('tasks')
        else :
            return HttpResponse('Pinga no creaste bien el usuario')
        
@login_required
def tasks(request):
    tasks = Task.objects.all()
    return render(request, 'tasks.html', {
        'tasks': tasks
    })

        
def logout(request):
    d_logout(request)
    return redirect('signup')


def login(request):
    form = AuthenticationForm()
    if request.method == 'GET':
        return render(request, 'login.html', {
            'form': form
        })
    else:
        try:
            user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
            if user is None:
                return render(request, 'login.html', {
                    'form': form,
                    'error': 'Usuario o contraseña incorrecta'
                })
                
            else:
                l_login(request, user)
                return redirect('tasks')
        except User.DoesNotExist:
            print('Usuario no existe')

@login_required
def create_task(request):


    if request.method == 'GET':
        form = TaskForm()
        return render(request, 'create_task.html', {
            'form': form
        })

    else:
        task = TaskForm(request.POST)
        print(task)

@login_required
def task_detail(request, task_id):

    if request.method == 'GET':

        task = get_object_or_404(Task, pk=task_id)
        form = TaskForm(instance=task)
        return render(request, 'task_detail.html', {
            'task': task,
            'form': form
        })
    
    else:
        try:
            task = get_object_or_404(Task, pk=task_id)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except Exception as e:
            print(e)
            return HttpResponse('Error al actualizar tarea')