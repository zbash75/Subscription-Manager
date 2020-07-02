from django import forms
from django_registration.forms import RegistrationForm
from .models import NewUser


# Form for users to enter account info to register
class NewUserForm(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        model = NewUser


# Form for Users to enter Login Information at Login Page
class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput())
