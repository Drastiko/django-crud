from django.shortcuts import render, redirect, get_object_or_404
from django.db import IntegrityError
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from tasks.forms import Task_form
from django.contrib.auth.decorators import login_required
from .models import Task
from django.utils import timezone

# Create your views here.
def home(request):
    return render(request, 'home.html')

def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html',{
        'form': UserCreationForm
    })
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('task')
            except IntegrityError:
                return render(request, 'signup.html',{
                    'form': UserCreationForm,
                    'error': 'Usuario ya registrado'
                })    
        return render(request, 'signup.html',{
                    'form': UserCreationForm,
                    'error': 'no coincieden las contraseñas'
                })
@login_required
def task(request):
    tasks = Task.objects.filter(user=request.user,completed__isnull=True)
    return render(request, 'task.html',{
        'tasks': tasks
    }) 

@login_required
def task_complete_view(request):
    tasks = Task.objects.filter(user=request.user,completed__isnull=False).order_by('-completed')
    return render(request, 'task.html',{
        'tasks': tasks
    }) 
    
@login_required
def task_detail(request,task_id):
    if request.method == 'GET':
        tasks = get_object_or_404(Task, pk=task_id, user=request.user)
        form = Task_form(instance=tasks)
        return render(request, 'taskDetail.html',{
            'tasks': tasks,
            'form': form
        })
    else:
        try:
            tasks = get_object_or_404(Task, pk=task_id, user=request.user)
            form = Task_form(request.POST, instance=tasks)
            form.save()
            return redirect('task')
        except ValueError:
            return render(request, 'taskDetail.html',{
            'tasks': tasks,
            'form': form,
            'error': 'Error de actualizacion'
        })

@login_required
def close_logout(request):
    logout(request)
    return redirect('home')



def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html',{
        'form': AuthenticationForm
        })
    else:
        usuario = authenticate(request, 
                            username=request.POST['username'],
                            password=request.POST['password'])
        if usuario is None:    
            return render(request, 'signin.html',{
            'form': AuthenticationForm,
            'error': 'Usuario y contraseña incorrectos'
            })
        else:
            login(request, usuario)
            return redirect('task')

@login_required    
def createdTask(request):
    if request.method == 'GET':
        return render(request,'createTask.html',{
        'form': Task_form 
    })
    else:
        try:
            forms = Task_form(request.POST)
            new_task = forms.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect('task')
        except ValueError:
            return render(request,'createTask.html',{
                'forms': Task_form,
                'error': 'Coloca datos validos'
            })
@login_required
def completeTask(request, task_id):
    tasks = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        tasks.completed = timezone.now()
        tasks.save()
        return redirect('task')

@login_required
def deleteTask(request, task_id):
   task = get_object_or_404(Task, pk=task_id, user=request.user)
   if request.method == 'POST':
       task.delete()
       return redirect('task')