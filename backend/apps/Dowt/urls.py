from django.urls import path
from backend.apps.Dowt.views import FinancialAdviceView, FinancialAdviceFromHistoryView, GetAdviceNumber

urlpatterns = [
    path("dowt/advice/", FinancialAdviceView.as_view(), name="advice from Dowt"),
    path("dowt/advice/detail/", FinancialAdviceFromHistoryView.as_view(), name="advice from Dowt history"),
    path("dowt/advice/remained/", GetAdviceNumber.as_view(), name="remained users advices"),
]
