from django.urls import path

from apps.total_balance.views import ViewTotalBalance, EditTotalBalance

urlpatterns = [
    path('total_balance/', ViewTotalBalance.as_view(), name='total_balance_view'),
    path('total_balance/<int:pk>/', EditTotalBalance.as_view(), name='total_balance_edit')
]
