from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *


class CustomUserCreationForm(UserCreationForm):
    is_staff = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = UserCreationForm.Meta.fields + ('is_staff',)


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'quantity', 'category']