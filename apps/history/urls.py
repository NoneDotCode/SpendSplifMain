from django.urls import path

from .views import *

urlpatterns = [
    path('my_history/', ViewHistory.as_view(), name='check_space_history')
]
