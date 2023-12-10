from rest_framework import serializers

from apps.space.models import Space, MemberPermissions


class SpaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Space
        fields = ("title", "members")


class AddAndRemoveMemberSerializer(serializers.Serializer):
    user_pk = serializers.IntegerField(write_only=True)
    fields = ("user_pk",)


class MemberPermissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberPermissions
        fields = '__all__'
