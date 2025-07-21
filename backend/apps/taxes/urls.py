from django.urls import path
from backend.apps.taxes.views import GenerateXMLAPIView

urlpatterns = [
    path('generate-xml/', GenerateXMLAPIView.as_view(), name='generate-xml'),
]