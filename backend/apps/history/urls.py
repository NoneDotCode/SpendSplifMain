from django.urls import path

from backend.apps.history.views import HistoryView, DailyIncomeView, ExpenseAutoDataView, IncomeAutoDataView, \
    TransferAutoDataView, StatisticView

urlpatterns = [
    path('my_history/', HistoryView.as_view(), name='check_space_history'),
    path('daily_income/', DailyIncomeView.as_view(), name='daily_income'),
    path('auto_income/', IncomeAutoDataView.as_view(), name='auto_data'),
    path('auto_expense/', ExpenseAutoDataView.as_view(), name='auto_data'),
    path('auto_transfer/', TransferAutoDataView.as_view(), name='transfer'),
    path('statistic/', StatisticView.as_view(), name='stat')
]
