from django.urls import path

from .views import *

urlpatterns = [
    path('space_accounts/', AllAccounts.as_view(), name='all_space_accounts'),
    path('edit_account/<int:pk>/', EditAccount.as_view(), name='edit_account'),
    path('create_account/', CreateAccount.as_view(),name='create_account'),
]
