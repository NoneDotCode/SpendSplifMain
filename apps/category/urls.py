from django.urls import path

from .views import *

urlpatterns = [
    path('create_category/', CreateCategory.as_view(), name='create_category'),
    path('my_categories/', AllCategory.as_view(), name='my_categories'),
    path('edit_category/<int:pk>/', EditCategory.as_view(), name='edit_category'),
    path('spend/', spend, name='spend_to_category'),
]
