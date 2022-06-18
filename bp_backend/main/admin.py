from django.contrib import admin
from .models import Category, Attribute,Profile

class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)

class AttributeAdmin(admin.ModelAdmin):
    list_display = ("category","name")

class ProfileAdmin(admin.ModelAdmin):
    list_display = ("spec",)

# Register your models here.

admin.site.register(Category, CategoryAdmin)
admin.site.register(Attribute, AttributeAdmin)
admin.site.register(Profile,ProfileAdmin)