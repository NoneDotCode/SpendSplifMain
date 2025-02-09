from django.urls import path
from backend.apps.cards.views import UserAuthView

urlpatterns = [
    path("o2/auth/", UserAuthView.as_view(), name="auth"),
]