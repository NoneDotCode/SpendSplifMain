from datetime import timezone

from rest_framework import generics
from backend.apps.notifications.serializers import UpdateViewersSerializer
from backend.apps.notifications.models import Notification, NotificationCompany
from rest_framework.response import Response
from django.utils.dateformat import DateFormat
from django.db.models import Value, CharField
from rest_framework import status
from django.utils.formats import date_format


class NotificationList(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        user = self.request.user

        notifications = Notification.objects.filter(who_can_view=user).exclude(seen=user).annotate(
            type=Value('notification', output_field=CharField())
        ).values('message', 'importance', 'created_at', 'type')

        company_notifications = NotificationCompany.objects.exclude(seen=user).annotate(
            type=Value('notification_company', output_field=CharField())
        ).values('message', 'importance', 'created_at', 'type')

        all_notifications = sorted(
            list(notifications) + list(company_notifications),
            key=lambda x: x['created_at'],
            reverse=True
        )

        formatted_notifications = [
            {
                'message': notification['message'],
                'importance': notification['importance'],
                'date': date_format(notification['created_at'], format="d F"),
                'time': date_format(notification['created_at'], format="H:i"),
                'type': notification['type']
            }
            for notification in all_notifications
        ]

        return Response(formatted_notifications)


class HowManyUnseen(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        user = self.request.user

        unseen_notifications = Notification.objects.filter(who_can_view=user).exclude(seen=user).count()
        unseen_company_notifications = NotificationCompany.objects.exclude(seen=user).count()

        total_unseen = unseen_notifications + unseen_company_notifications

        return Response({'unseen_count': total_unseen})


class UpdateSeen(generics.UpdateAPIView):
    serializer_class = UpdateViewersSerializer

    def get_object(self):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data['type'] == 'notification':
            return Notification.objects.get(id=serializer.validated_data['id'])
        return NotificationCompany.objects.get(id=serializer.validated_data['id'])

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        user = self.request.user
        instance = serializer.instance
        instance.seen.add(user)
        instance.save()


class SimulateNotification(generics.GenericAPIView):

    def post(self, request, *args, **kwargs):
        user = self.request.user
        Notification.objects.create(message="It is an important notification!",
                                    importance="important",
                                    created_at=timezone.utc).who_can_view.set([user,])
        Notification.objects.create(message="It is a medium important ~notification!~",
                                    importance="medium",
                                    created_at=timezone.utc).who_can_view.set([user,])
        Notification.objects.create(message="~It is~ a standard important notification!",
                                    importance="standard",
                                    created_at=timezone.utc).who_can_view.set([user,])
        NotificationCompany.objects.create(message="In our new update we added notifications!!!",
                                           importance="important",
                                           created_at=timezone.utc)
        return Response({'message': 'success'}, status=status.HTTP_201_CREATED)
