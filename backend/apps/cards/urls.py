from django.urls import path
from backend.apps.cards.views import (
    BankConnectionView,
    BankConnectionWebhook,
    BankTransactionsAndBalanceWebhook,
    BanksView,
    UserSpaceView
)

urlpatterns = [
    path('bank/connection/', BankConnectionView.as_view(), name='bank-connection'),
    path('banks/', BanksView.as_view(), name='czech-banks'),
    path('user-bank/', UserSpaceView.as_view(), name='user-space'),
    path('webhook/bank/connection/', BankConnectionWebhook.as_view(), name='bank-connection-webhook'),
    path('webhook/bank/transactions/', BankTransactionsAndBalanceWebhook.as_view(), name='bank-transactions-webhook'),
]