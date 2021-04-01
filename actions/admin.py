from .models import *
from django.contrib import admin
from django.contrib.auth.models import Group

# Register your models here.
admin.site.register(Setting)
admin.site.unregister(Group)
admin.site.register(Workspace)