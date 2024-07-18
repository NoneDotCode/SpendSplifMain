from django.urls import path

from backend.apps.history.views import HistoryView, ExpenseAutoDataView, IncomeAutoDataView, \
    TransferAutoDataView, StatisticView, StatisticSimulation, HistoryExpenseEditView, \
        HistoryIncomeEditView, HistoryPeriodView


urlpatterns = [
    path('my_history/', HistoryView.as_view(), name='check_space_history'),
    path('my_history/expenses/edit/<int:pk>/', HistoryExpenseEditView.as_view(), name='edit_history_expense'),
    path('my_history/incomes/edit/<int:pk>/', HistoryIncomeEditView.as_view(), name='edit_history_income'),
    path('auto_income/', IncomeAutoDataView.as_view(), name='auto_data'),
    path('auto_expense/', ExpenseAutoDataView.as_view(), name='auto_data'),
    path('auto_transfer/', TransferAutoDataView.as_view(), name='transfer'),
    path('statistic/', StatisticView.as_view(), name='stat'),
    path('statistic_simulation/', StatisticSimulation.as_view(), name='stat'),
    path('period/', HistoryPeriodView.as_view(), name='history_of_period')
]
