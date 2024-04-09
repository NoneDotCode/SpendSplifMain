from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenVerifyView

from backend.apps.customuser.views import CustomTokenObtainPairView, CustomTokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("apps.customuser.urls")),
    path("api/v1/", include("apps.space.urls")),
    path("api/v1/", include("apps.history.urls")),
    path("api/v1/my_spaces/<int:space_pk>/", include("apps.account.urls")),
    path("api/v1/my_spaces/<int:space_pk>/", include("apps.category.urls")),
    path("api/v1/my_spaces/<int:space_pk>/", include("apps.history.urls")),
    # JWT
    path("api/v1/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/v1/token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
