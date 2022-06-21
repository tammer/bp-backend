from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import BPUser

class BPUserCreationForm(UserCreationForm):

    class Meta:
        model = BPUser
        fields = ("username", "email")

class BPUserChangeForm(UserChangeForm):

    class Meta:
        model = BPUser
        fields = ("username", "email")