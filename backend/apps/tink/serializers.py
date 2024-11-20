from rest_framework import serializers
from backend.apps.tink.models import TinkAccount


class TinkAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = TinkAccount
        fields = "__all__"
