from datetime import timezone

from rest_framework import generics
from backend.apps.notifications.serializers import UpdateViewersSerializer
from backend.apps.notifications.models import Notification, NotificationCompany
from rest_framework.response import Response
from django.db.models import Value, CharField
from rest_framework import status
from django.utils.formats import date_format
from rest_framework.permissions import IsAuthenticated


class NotificationList(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = self.request.user

        count = request.data.get('count', 20)

        notifications = Notification.objects.filter(who_can_view=user).annotate(
            type=Value('notification', output_field=CharField())
        ).values('id', 'message', 'importance', 'created_at', 'type', 'seen')

        company_notifications = NotificationCompany.objects.all().annotate(
            type=Value('notification_company', output_field=CharField())
        ).values('id', 'message', 'importance', 'created_at', 'type', 'seen')

        all_notifications = sorted(
            list(notifications) + list(company_notifications),
            key=lambda x: x['created_at'],
            reverse=True
        )

        all_notifications = all_notifications[:count]

        formatted_notifications = []

        for notification in all_notifications:
            if type(notification["seen"]) is int:
                seen = (notification["seen"],)
            else:
                seen = notification["seen"]

            formatted_notifications = [
                {
                    'id': notification['id'],
                    'message': notification['message'],
                    'importance': notification['importance'].upper(),
                    'date': date_format(notification['created_at'], format="d F"),
                    'time': date_format(notification['created_at'], format="H:i"),
                    'type': notification['type'],
                    'seen': True if (notification['seen']) and (user in seen) else False
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
    permission_classes = (IsAuthenticated,)
    serializer_class = UpdateViewersSerializer

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        updated_notifications = []
        for item in serializer.validated_data['notifications']:
            if item['type'] == 'notification':
                instance = Notification.objects.get(id=item['id'])
            else:
                instance = NotificationCompany.objects.get(id=item['id'])

            self.perform_update(instance)
            updated_notifications.append({
                'id': instance.id,
                'type': item['type']
            })

        return Response(updated_notifications)

    def perform_update(self, instance):
        user = self.request.user
        instance.seen.add(user)
        instance.save()


class AllSeen(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = self.request.user

        notifications = Notification.objects.filter(who_can_view=user).exclude(seen=user)

        company_notifications = NotificationCompany.objects.all().exclude(seen=user)

        all_notifications = list(notifications) + list(company_notifications)

        for notification in all_notifications:
            notification.seen.add(user)
            notification.save()

        return Response({'Result:': "All notifications have been marked as seen successfully!"}, status=status.HTTP_200_OK)


class SimulateNotification(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

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
