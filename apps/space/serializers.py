from rest_framework import serializers

from .models import Space


class SpaceSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Space
        fields = ("title", "total_balance", "owner")
