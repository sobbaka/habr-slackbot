from .models import *
from django.contrib import admin
from django.contrib.auth.models import Group

# Register your models here.
# admin.site.register(Setting)
admin.site.unregister(Group)
admin.site.register(Workspace)

@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    fields = (
        'name',
        'greeting_text',
        'start_date',
        ('schedule_days',
        'schedule_hours'),
        'channels',
        'tags',
        'token',
        'first_launch'
    )