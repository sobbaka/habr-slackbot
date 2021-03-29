from django.urls import path
from .tasks import *

urlpatterns = [
    path('', sender),
]
