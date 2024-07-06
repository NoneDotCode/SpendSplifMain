from rest_framework import serializers


class FinancialDataSerializer(serializers.Serializer):
    income = serializers.DecimalField(max_digits=10, decimal_places=2)
    expenses = serializers.DecimalField(max_digits=10, decimal_places=2)
    categories = serializers.JSONField()
    recurring_payments = serializers.JSONField()
    goals = serializers.JSONField()
