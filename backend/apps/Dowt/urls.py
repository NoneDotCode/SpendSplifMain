from django.urls import path
from backend.apps.Dowt.views import FinancialAdviceView, FinancialAdviceFromHistoryView

urlpatterns = [
    path("dowt/advice/", FinancialAdviceView.as_view(), name="advice from Dowt"),
    path("dowt/advice/detail/", FinancialAdviceFromHistoryView.as_view(), name="advice from Dowt history")
]
