from django.shortcuts import render,redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
import ulid

from . import manager
from .models import Password


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return HttpResponseRedirect(reverse('p_manager:index'))
    else:
        form = UserCreationForm()
    return render(request, 'p_manager/signup.html', {'form': form})


@login_required
def update(request):
    return render(request, 'p_manager/update.html')


@login_required
def index(request):
    if request.method == 'POST':
        # for
        pass
    master_pass = 'test'
    operation = manager.DBOperation(master_pass)
    pw_model = Password.objects.filter(pw_user=request.user)
    pw_dict = []
    for i in pw_model:
        pw_dict.append({
            'id': i.pass_id,
            'password': operation.decrypt_pass(i.pw),
            'purpose': i.purpose,
            'description': i.description
        })
    return render(request, 'p_manager/index.html', {'pw_dict': pw_dict})


def auth_login(request):
    if request.user.is_authenticated:
        return redirect('p_manager:index')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            request.session['master_pass'] = username + password
            return render(request, 'p_manager/index.html')
        else:
            error_message = 'Username or password is invalid.'
            return render(request, 'p_manager/login.html', {'error_message': error_message})
    else:
        return render(request, 'p_manager/login.html')


@login_required
def auth_logout(request):
    logout(request)
    request.session.flush()
    return render(request, 'p_manager/login.html')


@login_required
def create_new_password(request):
    if request.method == "POST":
        pass_len = int(request.POST['len'])
        try:
            uppercase = int(request.POST['uppercase'])
        except KeyError:
            uppercase = 0
        try:
            symbol = int(request.POST['symbol'])
        except KeyError:
            symbol = 0
        password = manager.create_pass(pass_len=pass_len,
                                       uppercase=uppercase,
                                       symbol=symbol)
        print(password)

        return render(request, 'p_manager/add.html', {'password': password})
    else:
        return render(request, 'p_manager/create_pass.html')


@login_required
def add_pass(request):
    try:
        pass_id = ulid.new()
        master_pass = 'test'
        operation = manager.DBOperation(master_pass)
        e_pass = operation.encrypt_pass(request.POST['password'])
        pw_user = request.user
        Password.objects.create(pw_user=pw_user,
                                pass_id=pass_id,
                                pw=e_pass,
                                purpose=request.POST['purpose'],
                                description=request.POST['description'])
        return HttpResponseRedirect(reverse('p_manager:index'))

    except KeyError:
        return render(request, 'p_manager/add.html')
