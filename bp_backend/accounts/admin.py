from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import BPUserCreationForm, BPUserChangeForm
from .models import BPUser

class BPUserAdmin(UserAdmin):
    add_form = BPUserCreationForm
    form = BPUserChangeForm
    model = BPUser
    list_display = ["email", "username",]

admin.site.register(BPUser, BPUserAdmin)
