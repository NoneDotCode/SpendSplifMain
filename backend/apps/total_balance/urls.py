from django.urls import path

from backend.apps.total_balance.views import ViewTotalBalance

urlpatterns = [
    path('total_balance/', ViewTotalBalance.as_view(), name='total_balance_view'),
]
