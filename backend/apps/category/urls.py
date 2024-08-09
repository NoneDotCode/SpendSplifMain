from django.urls import path

from backend.apps.category.views import CreateCategory, ViewCategory, EditCategory, DeleteCategory, CategorizeExpense

urlpatterns = [
    path('create_category/', CreateCategory.as_view(), name='create_category'),
    path('my_categories/', ViewCategory.as_view(), name='my_categories'),
    path('my_categories/<int:pk>/', EditCategory.as_view(), name='edit_category'),
    path('delete_category/<int:pk>/', DeleteCategory.as_view(), name='delete_category'),
    path('categorize_expense/', CategorizeExpense.as_view(), name='categorize_expense'),
]
