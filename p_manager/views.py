from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import UpdateView
from django.utils.decorators import method_decorator

import ulid

from . import manager
from .models import Password
from .forms import PasswordForm


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('p_manager:index')
    else:
        form = UserCreationForm()
    return render(request, 'p_manager/signup.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class PasswordUpdateView(UpdateView):
    model = Password
    form_class = PasswordForm
    template_name = "p_manager/update.html"
    master_pass = 'test'
    operation = manager.DBOperation(master_pass)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(pw_user=self.request.user)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data()
        if self.request.method == 'GET':
            form = context_data['form']
            e_pass = form['pw'].value()
            d_pass = self.operation.decrypt_pass(e_pass)
            new_form = {'pw': d_pass,
                        'purpose': form['purpose'].value(),
                        'description': form['description'].value()}
            context_data['form'] = PasswordForm(new_form)
        return context_data

    def form_valid(self, form):
        post = form.save(commit=False)
        post.pw_user = self.request.user
        post.pw = self.operation.encrypt_pass(post.pw)
        post.save()
        return redirect('p_manager:index')


@login_required
def index(request):
    if request.method == 'POST':
        pw_id = request.POST["del_pw"]
        delete_pw = Password.objects.get(pass_id=pw_id)
        delete_pw.delete()

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
        return redirect('p_manager:index')

    except KeyError:
        return render(request, 'p_manager/add.html')
