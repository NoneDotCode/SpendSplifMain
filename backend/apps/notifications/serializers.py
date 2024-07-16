from rest_framework import serializers
from backend.apps.notifications.models import Notification, NotificationCompany


class UpdateViewersSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    type = serializers.ChoiceField(choices=[('notification', 'Notification'),
                                            ('notification_company', 'NotificationCompany')])

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'type': 'notification' if isinstance(instance, Notification) else 'notification_company'
        }


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
