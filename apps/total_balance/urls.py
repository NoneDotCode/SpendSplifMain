from django.urls import path

from apps.total_balance.views import TotalBalanceView

urlpatterns = [
    path('total_balance/', TotalBalanceView.as_view(), name='total_balance')
]
