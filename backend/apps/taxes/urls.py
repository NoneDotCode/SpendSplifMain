from django.urls import path
from backend.apps.taxes.views import GenerateXMLAPIView, GeneratePDFAPIView

urlpatterns = [
    path('generate-xml/', GenerateXMLAPIView.as_view(), name='generate-xml'),
    path('generate-pdf/', GeneratePDFAPIView.as_view(), name='generate-pdf'),
]