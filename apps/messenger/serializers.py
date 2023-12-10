from rest_framework import serializers
from .models import CustomUser, DmChat, DmMessage, MessageGroup, SpaceGroup

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
    father_chat = serializers.PrimaryKeyRelatedField(queryset=DmChat.objects.all(), required=False)

    class Meta:
        model = DmMessage
        fields = '__all__'


class MessageGroupSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()

    class Meta:
        model = MessageGroup
        fields = ['text', 'father_group', 'created_at', 'sender']

    def get_sender(self, obj):
        return obj.sender.username

    def save(self, **kwargs):
        self.validated_data['sender'] = kwargs.get('sender', None)
        return super().save(**kwargs)
