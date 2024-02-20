from django.urls import path
from .views import *

urlpatterns = [
    path('update_stocks/', UpdateStocksAPIView_group1.as_view(), name='update_stocks'),
    path('update_stocks_2/', UpdateStocksAPIView_group2.as_view(), name='update_stocks_2'),
    path('update_stocks_3/', UpdateStocksAPIView_group3.as_view(), name='update_stocks_3'),
    path('update_stocks_4/', UpdateStocksAPIView_group4.as_view(), name='update_stocks_4'),
    path('update_stocks_5/', UpdateStocksAPIView_group5.as_view(), name='update_stocks_5'),
    path('update_stocks_add/', Update_Stocks_APIView_group1_add.as_view(), name='update_stocks_add'),
    path('update_stocks_2_add/', UpdateStocksAPIView_group2_add.as_view(), name='update_stocks_2add'),
    path('update_stocks_3_add/', UpdateStocksAPIView_group3_add.as_view(), name='update_stocks_3add'),
    path('update_stocks_4_add/', UpdateStocksAPIView_group4_add.as_view(), name='update_stocks_4add'),
    path('update_stocks_5_add/', UpdateStocksAPIView_group5.as_view(), name='update_stocks_5add'),

    path('update_stocks_all/', StockAPIView.as_view(), name='get_all_stocks')
]
