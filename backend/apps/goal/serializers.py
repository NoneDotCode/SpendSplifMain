from rest_framework import serializers
from backend.apps.goal.models import Goal
from backend.apps.converter.utils import convert_number_to_letter


class GoalSerializer(serializers.ModelSerializer):
    format_collected = serializers.SerializerMethodField()

    class Meta:
        model = Goal
        fields = ('title', 'goal', 'collected', 'father_space', 'created', 'format_collected')

    @staticmethod
    def get_format_collected(obj):
        return convert_number_to_letter(obj.collected)
