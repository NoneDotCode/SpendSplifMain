from django.urls import path
from backend.apps.cards.views import (
    BankConnectionView,
    DeleteBankConnectionView,
    RefreshAccountView,
    DeleteBankAccountView,
    BanksView,
    UserSpaceView,
    SpaceBankConnectionsView,
    IsBankActionRequiredView,
    BankConnectionUpdateView
)

urlpatterns = [
    path('bank/connection/', BankConnectionView.as_view(), name='bank-connection'),
    path('banks/', BanksView.as_view(), name='czech-banks'),
    path('my_connections/', SpaceBankConnectionsView.as_view(), name='my-connections'),
    path('user-bank/', UserSpaceView.as_view(), name='user-space'),
    path('delete_bank_account/', DeleteBankAccountView.as_view(), name='account-connection-delete'),
    path('account/refresh/', RefreshAccountView.as_view(), name='refresh-account'),
    path('my_connections/action/', IsBankActionRequiredView.as_view(), name='is-bank-action-required'),
    path('my_connections/update/', BankConnectionUpdateView.as_view(), name='bank-update'),
    path('my_connections/delete/', DeleteBankConnectionView.as_view(), name='bank-delete'),
]
