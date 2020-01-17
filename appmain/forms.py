# \myclub_root\events\forms.py
from django import forms
from django.forms import ModelForm # events
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Pick  # events


class SignUpForm(UserCreationForm):
#    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
#    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.')
    phone_number = forms.DateField(help_text='Optional. Format: (xxx)xxx-xxxx')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'password1', 'password2', 'email',)


class PickForm(ModelForm):
    required_css_class = 'required'
    class Meta:
        model = Pick
        fields = '__all__'
