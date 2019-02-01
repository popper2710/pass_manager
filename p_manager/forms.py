from django import forms

from .models import Password
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class PasswordForm(forms.ModelForm):

    class Meta:
        
        model = Password
        fields = ("pw", "purpose", "description")


class SignupForm(UserCreationForm):
    email = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
