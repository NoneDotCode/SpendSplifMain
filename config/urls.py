from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("apps.customuser.urls")),
    path("api/v1/", include("apps.space.urls")),
    path("api/v1/", include("apps.account.urls")),
    path("api/v1/", include("apps.category.urls")),
    path('api/v1/', include("apps.history.urls")),
    path('api/v1/', include("apps.converter.urls")),
    path('api/v1/', include("apps.total_balance.urls")),
    # JWT
    path("api/v1/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/v1/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
