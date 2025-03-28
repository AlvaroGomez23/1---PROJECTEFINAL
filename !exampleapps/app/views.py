from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .models import Project, Task
from django.shortcuts import get_object_or_404
from .oldforms import createTask

# Create your views here.

def index(request):
    titulo = "Probar enviar datos a la vista"
    return render(request, 'index.html', {'titulo': titulo})

def hola(request, username):
    return HttpResponse("<h1>Hello world!</h1>" + username)
    

def pingaso(request):
    return render(request, "about.html")

def projects(request):
    projects = list(Project.objects.values()) 
    return JsonResponse(projects, safe=False)

def tasks(request):
    tasks = Task.objects.all()
    return render(request, "tasks.html", {'tasks': tasks})

def form1(request):

    if (request.method == 'GET'):
        return render(request, "form1.html", {
            'form': createTask()
        })
    else:
        Task.objects.create(title=request.POST['title'], description=request.POST['description'], project_id=1)
        return redirect('/home/tasks/')
    

# def createProject(request):
    
    