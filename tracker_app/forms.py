from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)  # Add email field

    class Meta:
        model = User
        # password1 and password2 are defaults in UserCreationForm.
        fields = ['username', 'email', 'password', 'password2']
