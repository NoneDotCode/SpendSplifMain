from django.urls import path

from backend.apps.history.views import HistoryView, DailyIncomeView

urlpatterns = [
    path('my_history/<int:space_pk>', HistoryView.as_view(), name='check_space_history'),
    path('daily_income/<int:space_pk>/', DailyIncomeView.as_view(), name='daily_income'),
]
