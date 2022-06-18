from django.contrib import admin
from .models import Category, Attribute

class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)

class AttributeAdmin(admin.ModelAdmin):
    list_display = ("category","name")

# Register your models here.

admin.site.register(Category, CategoryAdmin)
admin.site.register(Attribute, AttributeAdmin)