from django.urls import path
from backend.apps.cards.views import (
    BankConnectionView,
    BankConnectionWebhook,
    RefreshAccountView,
    DeleteBankAccountView,
    BanksView,
    UserSpaceView,
    SpaceBankConnectionsView
)

urlpatterns = [
    path('bank/connection/', BankConnectionView.as_view(), name='bank-connection'),
    path('banks/', BanksView.as_view(), name='czech-banks'),
    path('my_connections/', SpaceBankConnectionsView.as_view(), name='my-connections'),
    path('user-bank/', UserSpaceView.as_view(), name='user-space'),
    path('delete_bank_account/', DeleteBankAccountView.as_view(), name='account-connection-delete'),
    path('account/refresh/', RefreshAccountView.as_view(), name='refresh-account'),
]
