from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.generic import UpdateView
from django.utils.decorators import method_decorator

import ulid

from . import manager
from .models import Password
from .forms import PasswordForm, SignupForm


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            request.session['master_pass'] = request.POST['username'] + request.POST['password1']
            return redirect('p_manager:index')
    else:
        form = SignupForm()
    return render(request, 'p_manager/signup.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class PasswordUpdateView(UpdateView):
    model = Password
    form_class = PasswordForm
    template_name = "p_manager/update.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(pw_user=self.request.user)

    def get_context_data(self, **kwargs):
        master_pass = self.request.session['master_pass']
        operation = manager.DBOperation(master_pass)

        context_data = super().get_context_data()
        if self.request.method == 'GET':
            form = context_data['form']
            e_pass = form['pw'].value()
            d_pass = operation.decrypt_pass(e_pass)
            new_form = {'pw': d_pass,
                        'purpose': form['purpose'].value(),
                        'description': form['description'].value()}
            context_data['form'] = PasswordForm(new_form)
        return context_data

    def form_valid(self, form):
        post = form.save(commit=False)

        pw_dict = self.request.session['pw_dict']
        pk = self.kwargs['pk']
        for num, pw in enumerate(pw_dict):
            if pw['id'] == pk:
                pw_dict[num] = {'id': pk,
                                'password': post.pw,
                                'purpose': post.purpose,
                                'description': post.description}
        self.request.session['pw_dict'] = pw_dict

        post.pw_user = self.request.user
        master_pass = self.request.session['master_pass']
        operation = manager.DBOperation(master_pass)
        post.pw = operation.encrypt_pass(post.pw)
        post.save()

        return redirect('p_manager:index')


@method_decorator(login_required, name='dispatch')
class UserUpdateView(UpdateView):
    model = User
    fields = ('username', 'email',)
    template_name = 'p_manager/change_user.html'
    success_url = 'p_manager:change_user'

    def get_object(self):
        return self.request.user


@login_required
def index(request):
    try:
        pw_dict = request.session['pw_dict']
    except KeyError:
        pw_dict = None

    if request.method == 'POST':
        try:
            pw_id = request.POST["del_pw"]
        except KeyError:
            return redirect('p_manager:index')

        delete_pw = Password.objects.get(pass_id=pw_id)
        delete_pw.delete()

        for num, pw in enumerate(pw_dict):
            print(pw['id'])
            if pw['id'] == pw_id:
                pw_dict.pop(num)
                print('Delete Success')
        request.session['pw_dict'] = pw_dict

    master_pass = request.session['master_pass']
    operation = manager.DBOperation(master_pass)
    pw_model = Password.objects.filter(pw_user=request.user)

    if pw_dict is None:
        pw_dict = [{'id': i.pass_id,
                    'password': operation.decrypt_pass(i.pw),
                    'purpose': i.purpose,
                    'description': i.description
                    } for i in pw_model]
        request.session['pw_dict'] = pw_dict
        print(request.session['pw_dict'])

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
            return redirect('p_manager:index')
        else:
            error_message = 'Username or password is invalid.'
            return render(request, 'p_manager/login.html', {'error_message': error_message})
    else:
        return render(request, 'p_manager/login.html')


@login_required
def auth_logout(request):
    logout(request)
    request.session.flush()
    return redirect('p_manager:login')


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
        # print(password)

        return render(request, 'p_manager/add.html', {'password': password})
    else:
        return render(request, 'p_manager/create_pass.html')


@login_required
def add_pass(request):
    try:
        pass_id = ulid.new()
        master_pass = request.session['master_pass']
        operation = manager.DBOperation(master_pass)
        e_pass = operation.encrypt_pass(request.POST['password'])
        pw_user = request.user
        Password.objects.create(pw_user=pw_user,
                                pass_id=pass_id,
                                pw=e_pass,
                                purpose=request.POST['purpose'],
                                description=request.POST['description'])

        try:
            pw_dict = request.session['pw_dict']
        except KeyError:
            return redirect('p_manager:index')

        pw_dict.append({'id': pass_id.str,
                        'password': request.POST['password'],
                        'purpose': request.POST['purpose'],
                       'description': request.POST['description']
                        })
        request.session['pw_dict'] = pw_dict
        print(pw_dict)
        return redirect('p_manager:index')

    except KeyError:
        return render(request, 'p_manager/add.html')

