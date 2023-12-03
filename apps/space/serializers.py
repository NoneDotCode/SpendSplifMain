from rest_framework import serializers

from apps.space.models import Space


class SpaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Space
        fields = ("title", "members")


class AddMemberToSpaceSerializer(serializers.Serializer):
    user_pk = serializers.IntegerField(write_only=True)
    fields = ("user_pk",)
