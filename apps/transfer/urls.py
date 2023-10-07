from django.urls import path

from apps.transfer.views import TransferView

urlpatterns = [
    path("transfer/", TransferView.as_view(), name="transfers"),
]
