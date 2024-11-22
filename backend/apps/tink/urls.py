from django.urls import path

from backend.apps.tink.views import (FullIntegrationView, UpdateAccountsAndTransactions)

urlpatterns = [
    path('my_spaces/<int:space_pk>/full_integration/', FullIntegrationView.as_view(), name='full_integration_tink'),
    path('my_spaces/<int:space_pk>/update_accounts_and_transactions/', UpdateAccountsAndTransactions.as_view(),
         name='update_accounts_and_transactions_tink')
]
