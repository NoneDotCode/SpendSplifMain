from rest_framework import serializers

from backend.apps.history.models import HistoryIncome
from backend.apps.space.models import Space, MemberPermissions


class SpaceSerializer(serializers.ModelSerializer):
    members_count = serializers.SerializerMethodField()

    class Meta:
        model = Space
        fields = ("id", "title", "currency", "members_count")

    @staticmethod
    def get_members_count(obj):
        return obj.members.count()

class SpaceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Space
        fields = ("id", "title", "currency", "members")


class AddAndRemoveMemberSerializer(serializers.Serializer):
    user_pk = serializers.IntegerField(write_only=True)
    fields = ("user_pk",)


class MemberPermissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberPermissions
        fields = '__all__'
