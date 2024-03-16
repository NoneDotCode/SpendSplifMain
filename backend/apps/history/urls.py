from django.urls import path

from backend.apps.history.views import HistoryView, ExpenseAutoDataView, IncomeAutoDataView, \
    TransferAutoDataView, CategoryStatisticView, IncomeStatisticView, ExpensesStatisticView, StatisticView, \
    GoalTransferStatisticView

urlpatterns = [
    path('my_history/', HistoryView.as_view(), name='check_space_history'),
    path('auto_income/', IncomeAutoDataView.as_view(), name='auto_data'),
    path('auto_expense/', ExpenseAutoDataView.as_view(), name='auto_data'),
    path('auto_transfer/', TransferAutoDataView.as_view(), name='transfer'),
    path('statistic/', StatisticView.as_view(), name='stat'),
    path('statistic_category/', CategoryStatisticView.as_view(), name='stat'),
    path('statistic_income/', IncomeStatisticView.as_view(), name='stat'),
    path('statistic_expenses/', ExpensesStatisticView.as_view(), name=''),
    path('statistic_goals/', GoalTransferStatisticView.as_view(), name=''),
]
