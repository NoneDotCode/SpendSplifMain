from django.urls import path

from .views import *

urlpatterns = [
    path('check_history/', ViewHistory.as_view(), name='check_space_history')
]
