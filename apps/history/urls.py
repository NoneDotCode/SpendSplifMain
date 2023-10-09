from django.urls import path

from apps.history.views import HistoryView

urlpatterns = [
    path('my_history/', HistoryView.as_view(), name='check_space_history')
]
