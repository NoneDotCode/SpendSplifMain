from rest_framework import generics
from backend.apps.notifications.serializers import UpdateViewersSerializer
from backend.apps.notifications.models import Notification, NotificationCompany
from rest_framework.response import Response
from django.utils.dateformat import DateFormat
from django.db.models import Value, CharField


class NotificationList(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        user = self.request.user

        notifications = Notification.objects.filter(who_can_view=user).exclude(seen=user).annotate(
            type=Value('notification', output_field=CharField())
        ).values('message', 'color', 'created_at', 'type')

        company_notifications = NotificationCompany.objects.exclude(seen=user).annotate(
            type=Value('notification_company', output_field=CharField())
        ).values('message', 'color', 'created_at', 'type')

        all_notifications = sorted(
            list(notifications) + list(company_notifications),
            key=lambda x: x['created_at'],
            reverse=True
        )

        formatted_notifications = [
            {
                'message': notification['message'],
                'color': notification['color'],
                'created_at': DateFormat(notification['created_at']).format('d-m-Y'),
                'type': notification['type']
            }
            for notification in all_notifications
        ]

        return Response(formatted_notifications)


class HowManyUnseen(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        user = self.request.user

        unseen_notifications = Notification.objects.filter(who_can_view=user).exclude(seen=user).count()
        unseen_company_notifications = NotificationCompany.objects.filter(who_can_view=user).exclude(seen=user).count()

        total_unseen = unseen_notifications + unseen_company_notifications

        return Response({'unseen_count': total_unseen})


class UpdateSeen(generics.UpdateAPIView):
    serializer_class = UpdateViewersSerializer

    def get_queryset(self):
        if self.request.data.get('type') == 'notification':
            return Notification.objects.all()
        return NotificationCompany.objects.all()

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
