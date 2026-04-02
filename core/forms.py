from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django import forms

class Registro(UserCreationForm):
    
    class Meta(UserCreationForm.Meta):
        model = User 
        fields = ("email","username","password1" , "password2")

