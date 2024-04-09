from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenVerifyView

from backend.apps.customuser.views import CustomTokenObtainPairView, CustomTokenRefreshView

base_space_url = "api/v1/my_spaces/<int:space_pk>/"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("apps.customuser.urls")),
    path("api/v1/", include("apps.space.urls")),
    path("api/v1/", include("apps.api_stocks.urls")),
    path("api/v1/", include("apps.cryptocurrency.urls")),
    path(base_space_url, include("apps.account.urls")),
    path(base_space_url, include("apps.category.urls")),
    path(base_space_url, include("apps.history.urls")),
    path(base_space_url, include("apps.total_balance.urls")),
    path(base_space_url, include("apps.goal.urls")),
    path(base_space_url, include("apps.spend.urls")),
    path(base_space_url, include("apps.transfer.urls")),

    # JWT
    path("api/v1/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/v1/token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
