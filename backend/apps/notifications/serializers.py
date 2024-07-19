from rest_framework import serializers
from backend.apps.notifications.models import Notification, NotificationCompany


class NotificationItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    type = serializers.ChoiceField(choices=[('notification', 'Notification'),
                                            ('notification_company', 'NotificationCompany')])


class UpdateViewersSerializer(serializers.Serializer):
    notifications = NotificationItemSerializer(many=True)


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
