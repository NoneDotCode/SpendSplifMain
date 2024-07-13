from rest_framework import serializers

class TransferSerializer(serializers.Serializer):
    from_object = serializers.CharField()
    to_object = serializers.CharField()
    # amount = serializers.IntegerField()

class TransferGoalToAccSerializer(serializers.Serializer):
    amount = serializers.IntegerField()
    from_goal = serializers.IntegerField()
    to_account = serializers.IntegerField()

class TransferAccToGoalSerializer(serializers.Serializer):
    to_goal = serializers.IntegerField()
    from_account = serializers.IntegerField()
    amount = serializers.IntegerField()
    
class TransferAccToAccSerializer(serializers.Serializer):
    to_account = serializers.IntegerField()
    from_account = serializers.IntegerField()
    amount = serializers.IntegerField()