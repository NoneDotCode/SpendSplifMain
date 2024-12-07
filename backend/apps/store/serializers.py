from rest_framework import serializers
from .models import PaymentHistory

class PaymentHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentHistory
        fields = ['space_id', 'payment_category', 'amount', 'date']