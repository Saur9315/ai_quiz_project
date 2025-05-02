from django import forms
from django.contrib.auth.forms import UserChangeForm
from .models import CustomUser

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password']


class CustomUserChangeForm(UserChangeForm):
    birthdate = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text='',
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'birthdate', 'country', 'city')

    exclude = ['password']
    username = forms.CharField(help_text='')
    email = forms.EmailField(help_text='')
    first_name = forms.CharField(help_text='')
    last_name = forms.CharField(help_text='')
    