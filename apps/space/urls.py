from django.urls import path

from .views import *

urlpatterns = [
    path('create_space/', CreateSpace.as_view(), name='create_space'),
    path('my_spaces/', AllSpaces.as_view(), name='my_spaces'),
]
