from django.urls import path
from backend.apps.api_stocks.views import *

urlpatterns = [
    path('update_stocks/', UpdateStocksAPIViewGroupFirst.as_view(), name='update_stocks'),
    path('update_stocks_2/', UpdateStocksAPIViewGroupSecond.as_view(), name='update_stocks_2'),
    path('update_stocks_3/', UpdateStocksAPIViewGroupThird.as_view(), name='update_stocks_3'),
    path('update_stocks_4/', UpdateStocksAPIViewGroupFourth.as_view(), name='update_stocks_4'),
    path('update_stocks_5/', UpdateStocksAPIViewGroupFifth.as_view(), name='update_stocks_5'),
    path('update_stocks_add/', UpdateStocksAPIViewGroupFirstAdd.as_view(), name='update_stocks_add'),
    path('update_stocks_2_add/', UpdateStocksAPIViewGroupSecondAdd.as_view(), name='update_stocks_2add'),
    path('update_stocks_3_add/', UpdateStocksAPIViewGroupThirdAdd.as_view(), name='update_stocks_3add'),
    path('update_stocks_4_add/', UpdateStocksAPIViewGroupFourthAdd.as_view(), name='update_stocks_4add'),
    path('update_stocks_5_add/', UpdateStocksAPIViewGroupFifth.as_view(), name='update_stocks_5add'),

    path('get_stocks_all/', StockAPIView.as_view(), name='get_all_stocks'),
    path('add_all_stocks/', GenerateRandomStockDataView.as_view(), name='add_all_stocks')
]
