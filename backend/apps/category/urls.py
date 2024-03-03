from django.urls import path

from backend.apps.category.views import CreateCategory, ViewCategory, EditCategory, DeleteCategory, SpendView

urlpatterns = [
    path('create_category/', CreateCategory.as_view(), name='create_category'),
    path('my_categories/', ViewCategory.as_view(), name='my_categories'),
    path('my_categories/<int:pk>/', EditCategory.as_view(), name='edit_category'),
    path('delete_category/<int:pk>/', DeleteCategory.as_view(), name='delete_category'),
    path('my_categories/<int:pk>/spend/', SpendView.as_view(), name='spend')
]
