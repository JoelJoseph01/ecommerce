from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

class SignUp(UserCreationForm):
    email=forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ['email','username','password1','password2']

    def clean(self):
       email = self.cleaned_data.get('email')
       return self.cleaned_data