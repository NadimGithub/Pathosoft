from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import CustomUser
import re

class RegisterForm(UserCreationForm):
    full_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    mobile_no = forms.CharField(max_length=15, required=True)

    class Meta:
        model = CustomUser
        fields = ['full_name', 'username', 'email', 'mobile_no', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("Email already exists.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError("Username already taken.")
        return username

    def clean_mobile_no(self):
        mobile_no = self.cleaned_data.get('mobile_no')
        if not re.match(r'^\d{10}$', mobile_no):
            raise ValidationError("Mobile number must be exactly 10 digits.")
        if CustomUser.objects.filter(mobile_no=mobile_no).exists():
            raise ValidationError("Mobile number already registered.")
        return mobile_no


class LoginForm(forms.Form):
    username_or_email = forms.CharField(label='Username or Email', required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean_username_or_email(self):
        data = self.cleaned_data.get('username_or_email')
        if not data:
            raise ValidationError("This field is required.")
        return data


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['full_name', 'username', 'email', 'mobile_no', 'lab', 'role',
                  'password1', 'password2', 'qualification', 'address','profile_image']

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        lab = cleaned_data.get('lab')

        if role != 'admin' and not lab:
            raise ValidationError("Non-admin users must be assigned to a Lab.")
        return cleaned_data


class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['full_name', 'username', 'email', 'mobile_no', 'lab', 'role',
                  'qualification', 'address','profile_image']

    def clean_mobile_no(self):
        mobile_no = self.cleaned_data.get('mobile_no')
        if not re.match(r'^\d{10}$', mobile_no):
            raise ValidationError("Enter a valid mobile number.")
        return mobile_no
