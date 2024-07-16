from rest_framework import serializers
from backend.apps.notifications.models import Notification, NotificationCompany


class UpdateViewersSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    type = serializers.ChoiceField(choices=[('notification', 'Notification'),
                                            ('notification_company', 'NotificationCompany')])

    def update(self, instance, validated_data):
        user = self.context["request"].user

        if validated_data['type'] == 'notification':
            notification = Notification.objects.get(id=validated_data['id'])
        else:
            notification = NotificationCompany.objects.get(id=validated_data['id'])

        notification.seen.add(user)
        notification.save()

        return notification


class NotificationSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ("type", "message", "color", "created_at")

    @staticmethod
    def get_type():
        return 'notification'


class NotificationCompanySerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()

    class Meta:
        model = NotificationCompany
        fields = ("type", "message", "color", "created_at")

    @staticmethod
    def get_type():
        return 'notification_company'
