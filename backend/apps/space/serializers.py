from rest_framework import serializers

from backend.apps.history.models import HistoryIncome
from backend.apps.space.models import Space, MemberPermissions


class SpaceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Space
        fields = ("title", "currency", "members")


class SpaceListSerializer(serializers.ModelSerializer):
    members_count = serializers.SerializerMethodField()
    can_edit_permissions = serializers.SerializerMethodField()

    class Meta:
        model = Space
        fields = ("id", "title", "currency", "members_count", "can_edit_permissions")

    @staticmethod
    def get_members_count(obj):
        return obj.members.count()

    def get_can_edit_permissions(self, obj):
        request = self.context.get('request')
        if not request or not request.user:
            return False
        return (obj.memberpermissions_set.filter(member=request.user, edit_members=True).exists() or
                obj.memberpermissions_set.filter(member=request.user, owner=True).exists())


class AddAndRemoveMemberSerializer(serializers.Serializer):
    user_pk = serializers.IntegerField(write_only=True)
    fields = ("user_email",)


class MemberPermissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberPermissions
        fields = '__all__'
