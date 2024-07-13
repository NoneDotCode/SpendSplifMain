from django.urls import path, include
from backend.apps.notifications.views import NotificationList, HowManyUnseen, UpdateSeen

urlpatterns = [
    path("notifications/list/", NotificationList.as_view(), name="notification_list"),
    path("notifications/unseen_count/", HowManyUnseen.as_view(), name="unseen_count"),
    path("notifications/update_viewer/", UpdateSeen.as_view(), name="update_viewer"),
]
