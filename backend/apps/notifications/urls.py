from django.urls import path, include
from backend.apps.notifications.views import NotificationList, HowManyUnseen, UpdateSeen, SimulateNotification

urlpatterns = [
    path("notifications/list/", NotificationList.as_view(), name="notification_list"),
    path("notifications/unseen_count/", HowManyUnseen.as_view(), name="unseen_count"),
    path("notifications/update_viewer/", UpdateSeen.as_view(), name="update_viewer"),
    path("notifications/simulate/", SimulateNotification.as_view(), name="simulate_notification")
]
