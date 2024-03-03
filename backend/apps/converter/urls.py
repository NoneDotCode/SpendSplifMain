from django.urls import path

from backend.apps.converter.views import ConvertCurrencyView

urlpatterns = [
    path('convert/', ConvertCurrencyView.as_view(), name='converter')
]
