from django.urls import path

from apps.settings.views import EditCustomUser

urlpatterns = [
    path("settings/customuser/<int:pk>/", EditCustomUser.as_view(), name="сonfidentially"),
]
