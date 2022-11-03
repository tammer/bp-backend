from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import BPUserCreationForm, BPUserChangeForm
from .models import BPUser, Invite

class BPUserAdmin(UserAdmin):
    add_form = BPUserCreationForm
    form = BPUserChangeForm
    model = BPUser
    list_display = ["email", "username", "date_joined", "last_login"]

class InviteAdmin(admin.ModelAdmin):
    list_display: ("email","code","created_by","created_at","accepted_by")    

admin.site.register(BPUser, BPUserAdmin)
admin.site.register(Invite, InviteAdmin )