from rest_framework import serializers
from backend.apps.tickets.models import Ticket, TicketMessage

class CreateTicketSerializer(serializers.ModelSerializer):
    space_pk = serializers.IntegerField(required=False)

    class Meta:
        model = Ticket
        fields = ("id", "help_in_space","space_pk", "message")
    def save(self, validated_data):
        user = self.context['request'].user 


        Ticket.objects.create(
            user=user,
            help_in_space=validated_data.get("help_in_space", False),
            space_pk = validated_data.get("space_pk", None),
            message = validated_data.get("message"),
            chat=None,
        )

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = "__all__"

class TicketMessageSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TicketMessage
        fields = ('text',)