from rest_framework import serializers
from .models import CustomUser, DmChat, DmMessage

from rest_framework import serializers
from apps.messenger.models import DmChat, CustomUser


class DmChatSerializer(serializers.ModelSerializer):
    owner_1 = serializers.SlugRelatedField(
        queryset=CustomUser.objects.all(),
        slug_field='username'
    )
    owner_2 = serializers.SlugRelatedField(
        queryset=CustomUser.objects.all(),
        slug_field='username'
    )

    class Meta:
        model = DmChat
        fields = ['owner_1', 'owner_2']


class DmMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DmMessage
        fields = ['id', 'text', 'created_at', 'father_chat', 'sender']


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DmMessage
        fields = '__all__'


class DmMessageSerializer(serializers.ModelSerializer):
    father_chat = serializers.PrimaryKeyRelatedField(queryset=DmChat.objects.all(), required=False)

    class Meta:
        model = DmMessage
        fields = '__all__'
