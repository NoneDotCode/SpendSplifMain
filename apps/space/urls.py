from django.urls import path

from .views import CreateSpace

urlpatterns = [
    path('create_space/', CreateSpace.as_view(), name='create_space')
]
