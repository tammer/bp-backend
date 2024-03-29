from django.contrib import admin
from .models import Assessment, Category, Attribute, Job, Opportunity,Profile,Skill,Anchor,Endorsement,Log

class AnchorAdmin(admin.ModelAdmin):
    list_display: ("passer",)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)

class AttributeAdmin(admin.ModelAdmin):
    list_display = ("category","name")

class ProfileAdmin(admin.ModelAdmin):
    list_display = ("owner","spec",)

class SkillAdmin(admin.ModelAdmin):
    list_display: ("name",)

class AssessmentAdmin(admin.ModelAdmin):
    list_display: ("skill")

class EndorsementAdmin(admin.ModelAdmin):
    list_display: ("owner")

class JobAdmin(admin.ModelAdmin):
    list_display: ("id")

class OpportunityAdmin(admin.ModelAdmin):
    list_display: ("id")

class LogAdmin(admin.ModelAdmin):
    list_display = ("created_at","value",)

# Register your models here.

admin.site.register(Category, CategoryAdmin)
admin.site.register(Attribute, AttributeAdmin)
admin.site.register(Profile,ProfileAdmin)
admin.site.register(Skill,SkillAdmin)
admin.site.register(Anchor,AnchorAdmin)
admin.site.register(Assessment,AssessmentAdmin)
admin.site.register(Endorsement,EndorsementAdmin)
admin.site.register(Job,JobAdmin)
admin.site.register(Opportunity,OpportunityAdmin)
admin.site.register(Log,LogAdmin)
