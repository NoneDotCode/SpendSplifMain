from django.urls import path
from backend.apps.excel.views import ExportHistoryView, ImportHistoryView

urlpatterns = [
    path('export_history/', ExportHistoryView.as_view(), name='export-history'),
    path('import_history/', ImportHistoryView.as_view(), name='import-history')
]
