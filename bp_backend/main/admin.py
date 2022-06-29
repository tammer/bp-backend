from django.contrib import admin
from .models import Assessment, Category, Attribute,Profile,Level,Skill,Anchor

class AnchorAdmin(admin.ModelAdmin):
    list_display: ("passer",)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)

class AttributeAdmin(admin.ModelAdmin):
    list_display = ("category","name")

class ProfileAdmin(admin.ModelAdmin):
    list_display = ("spec",)

class LevelAdmin(admin.ModelAdmin):
    list_display: ("id","name")

class SkillAdmin(admin.ModelAdmin):
    list_display: ("name",)

class AssessmentAdmin(admin.ModelAdmin):
    list_display: ("skill")

# Register your models here.

admin.site.register(Category, CategoryAdmin)
admin.site.register(Attribute, AttributeAdmin)
admin.site.register(Profile,ProfileAdmin)
admin.site.register(Level, LevelAdmin)
admin.site.register(Skill,SkillAdmin)
admin.site.register(Anchor,AnchorAdmin)
admin.site.register(Assessment,AssessmentAdmin)
