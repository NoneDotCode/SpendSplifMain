from rest_framework import serializers
from backend.apps.tickets.models import Ticket, TicketMessage

class CreateTicketSerializer(serializers.ModelSerializer):
    space_pk = serializers.IntegerField(required=False)
    class Meta:
        model = Ticket
        fields = ("id", "help_in_space","space_pk", "message", "title")
    def save(self, validated_data):
        user = self.context['request'].user 


        Ticket.objects.create(
            user=user,
            help_in_space=validated_data.get("help_in_space", False),
            space_pk = validated_data.get("space_pk", None),
            title = validated_data.get("title"),
            message = validated_data.get("message"),
            chat=None,
        )

class TicketSerializer(serializers.ModelSerializer):
    employee = serializers.EmailField(source='employee.email', read_only=True)
    unseen = serializers.SerializerMethodField()
    
    class Meta:
        model = Ticket
        fields = "__all__"

    def get_unseen(self, obj):
        if obj.status != 'in_process' or not obj.chat:
            return 0
        
        user = self.context['request'].user 
        
        # Подсчитываем количество непросмотренных сообщений (seen=False)
        # для текущего пользователя (считаем сообщения от другого участника чата)
        unseen_count = TicketMessage.objects.filter(
            father_chat=obj.chat,
            seen=False,
            sender__in=[obj.user if user == obj.employee else obj.employee]
        ).count()
        
        return unseen_count
    

class TicketSerializer2(serializers.ModelSerializer):
    employee = serializers.EmailField(source='employee.email', read_only=True)
    
    class Meta:
        model = Ticket
        fields = "__all__"


class TicketMessageSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TicketMessage
        fields = ('text',)