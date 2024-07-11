from rest_framework import serializers
from backend.apps.converter.utils import convert_number_to_letter
from backend.apps.goal.models import Goal
from backend.apps.space.models import Space


class GoalSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    father_space = serializers.PrimaryKeyRelatedField(queryset=Space.objects.all())
    collected_percentage = serializers.SerializerMethodField()
    created_date = serializers.DateField(format="%d.%m.%Y", read_only=True)
    created_time = serializers.TimeField(format="%H:%M", read_only=True)
    goal_converted = serializers.SerializerMethodField()
    collected_converted = serializers.SerializerMethodField()

    class Meta:
        model = Goal
        fields = ('id', 'title', 'goal', 'goal_converted', 'collected', 'collected_converted',
                  'father_space', 'collected_percentage', 'created_date', 'created_time')

    @staticmethod
    def get_collected_percentage(obj):
        return f"{round(obj.collected_percentage, 2)}%"

    @staticmethod
    def get_goal_converted(obj):
        return convert_number_to_letter(float(obj.goal))

    @staticmethod
    def get_collected_converted(obj):
        return convert_number_to_letter(float(obj.collected))
