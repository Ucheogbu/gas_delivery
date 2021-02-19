from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.contrib.auth import get_user_model
# from .models import UserData
# import re


UserData = get_user_model()


class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = UserData
        fields = ('first_name', 'last_name', 'username', 'email', 'user_id', 'address', 'state', 'country')


class CustomUserChangeForm(UserChangeForm):

    class Meta(UserChangeForm):
        model = UserData
        fields = ('first_name', 'last_name', 'username', 'email', 'user_id', 'address', 'state', 'country')


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'inputEmail',
                                                             'placeholder': 'Email Address'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'inputPassword',
                                                                 'placeholder': 'Password'}))
