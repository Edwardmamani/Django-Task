from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import get_object_or_404

from .forms import TaskForm
from .models import Task

from django.utils import timezone
from django.contrib.auth.decorators import login_required
# Create your views here.


def home(request):
    title = "Acerca de nosotros"

    return render(request, 'home.html', {
        'title': title
    })
    # return HttpResponse("Hello world")


@login_required
def tasks(request):
    # tasks = Task.objects.all()
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=True)

    return render(request, 'tasks.html', {
        'tasks': tasks,
        'titulo': "Task Pending"
    })


def signup(request):
    if request.method == 'GET':
        print('enviado formulario')
        return render(request, 'signup.html', {
            'form': UserCreationForm
        })

    else:
        print('Opteniedo datos')
        if request.POST['password1'] == request.POST['password2']:
            # REGISTRANDO USUSARIO

            try:
                print(request.POST['username'])
                user = User.objects.create_user(
                    username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('tasks')
                # return render(request, 'tasks.html')
            except IntegrityError:  # CONSIDERAR A UN ERROR ESPECIFICO
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    'error': "USUARIO YA ESXITE"
                })

        return render(request, 'signup.html', {
            'form': UserCreationForm,
            'error': "las contraseñas no coindiden"
        })


# ///////////CIERRA LA SESION////////////
@login_required
def signout(request):
    logout(request)
    return redirect('home')


def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm
        })
    else:

        print(request.POST)
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': "Usuario o Contraseña no encontrada"
            })
        else:
            login(request, user)
            return redirect('tasks')


@login_required
def crete_task(request):
    if request.method == 'GET':
        return render(request, 'create_task.html', {
            'form': TaskForm,
            'error': "Inpriendo formulario"
        })
    else:
        try:
            # print(request.POST)
            form = TaskForm(request.POST)
            # print(form)
            new_task = form.save(commit=False)
            new_task.user = request.user  # el usuario de la tarea es
            print(new_task)
            new_task.save()
            return redirect('tasks')
            # return render(request, 'tasks.html', {
            #     'form': TaskForm
            # })
            # ////////////////////////////
        except ValueError:
            return render(request, 'create_task.html', {
                'form': TaskForm,
                'error': "Please provide valida data",
            })


@login_required
def task_detail(request, task_id):
    if request.method == 'GET':
        print(task_id)
        # task=Task.objects.get(pk=task_id)
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        form = TaskForm(instance=task)
        return render(request, 'task_detail.html', {
            'task': task,
            'form': form,
        })
    else:
        try:
            print(request.POST)
            # en esta instacia modifica la tarea de esta forma
            task = get_object_or_404(Task, pk=task_id)
            form = TaskForm(request.POST, instance=task)
            # Guarda la tarea
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detail.html', {
                'task': task,
                'form': form,
                'error': "ERROR UPDATING TASK"
            })


@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)

    if request.method == 'POST':
        task.datecompleted = timezone.now()
        print(task.datecompleted)
        task.save()
        return redirect('tasks')


@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delte()
        return redirect('tasks')


@login_required
def tasks_complete(request):

    tasks = Task.objects.filter(
        user=request.user, datecompleted__isnull=False).order_by('-datecompleted')

    return render(request, 'tasks.html', {
        'tasks': tasks,
        'titulo': "Tasks Complete",
    })
