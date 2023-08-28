from django.urls import path

from apps.converter.views import ConvertCurrencyView

urlpatterns = [
    path('convert/', ConvertCurrencyView.as_view(), name='converter')
]
