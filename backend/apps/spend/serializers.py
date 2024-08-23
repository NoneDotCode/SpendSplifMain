from django_celery_beat.models import PeriodicTask

from rest_framework import serializers


class SpendSerializer(serializers.Serializer):
    account_pk = serializers.IntegerField(required=True)
    category_pk = serializers.IntegerField(required=False)
    amount = serializers.IntegerField(required=True)
    comment = serializers.CharField(required=False)


class PeriodicSpendCreateSerializer(serializers.Serializer):
    account_pk = serializers.IntegerField(required=True)
    category_pk = serializers.IntegerField(required=True)
    amount = serializers.FloatField(required=True)
    title = serializers.CharField(required=True)
    hour = serializers.CharField(required=False, default="13")
    minute = serializers.CharField(required=False, default="40")
    day_of_week = serializers.CharField(required=False, default="*")
    day_of_month = serializers.CharField(required=False, default="*")
    month_of_year = serializers.CharField(required=False, default="*")


class PeriodicSpendEditSerializer(serializers.Serializer):
    account_pk = serializers.IntegerField(required=False, default=None)
    category_pk = serializers.IntegerField(required=False, default=None)
    amount = serializers.FloatField(required=False, default=None)
    title = serializers.CharField(required=False, default=None)
    hour = serializers.CharField(required=False, default=None)
    minute = serializers.CharField(required=False, default=None)
    day_of_week = serializers.CharField(required=False, default=None)
    day_of_month = serializers.CharField(required=False, default=None)
    month_of_year = serializers.CharField(required=False, default=None)
