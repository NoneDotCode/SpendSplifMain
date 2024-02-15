from django.urls import path
from .views import UpdateStocksAPIView

urlpatterns = [
    path('update_stocks/', UpdateStocksAPIView.as_view(), name='update_stocks'),
]
