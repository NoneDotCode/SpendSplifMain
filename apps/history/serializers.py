from rest_framework import serializers

from apps.history.models import History


class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = ('number', 'currency', 'comment', 'from_acc', 'to_cat')
