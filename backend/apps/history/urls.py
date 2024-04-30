from django.urls import path

from backend.apps.history.views import HistoryView, DailyIncomeView, AutoDataView, HistoryExpenseEdit, HistoryIncomeEdit

urlpatterns = [
    path('my_history/', HistoryView.as_view(), name='check_space_history'),
    path('daily_income/', DailyIncomeView.as_view(), name='daily_income'),
    path('auto_data/', AutoDataView.as_view(), name='auto_data'),
    path("edit_expense/<int:pk>/", HistoryExpenseEdit.as_view(), name="edit_expense"),
    path("edit_income/<int:pk>/", HistoryIncomeEdit.as_view(), name="edit_income"),
]
