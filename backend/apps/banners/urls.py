from django.urls import path
from backend.apps.banners.views import BannerUploadView, RandomBannerView, BannerClickView

urlpatterns = [
    path('upload-banner/', BannerUploadView.as_view(), name='upload-banner'),
    path('get-random-banner/', RandomBannerView.as_view(), name='get-random-banner'),
    path('click-banner/<int:banner_id>/', BannerClickView.as_view(), name='click-banner'),
]
