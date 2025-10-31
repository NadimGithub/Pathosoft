from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class RegisterForm(UserCreationForm):
    full_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    mobile_no = forms.CharField(max_length=15)

    class Meta:
        model = CustomUser
        fields = ['full_name', 'username', 'email', 'mobile_no', 'password1', 'password2']


class LoginForm(forms.Form):
    username_or_email = forms.CharField(label='Username or Email')
    password = forms.CharField(widget=forms.PasswordInput)

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['full_name', 'username', 'email', 'mobile_no', 'lab', 'role', 'password1', 'password2']

class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['full_name', 'username', 'email', 'mobile_no', 'lab']