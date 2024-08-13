from rest_framework import serializers
from backend.apps.converter.utils import convert_number_to_letter
from backend.apps.goal.models import Goal
from backend.apps.space.models import Space
from django.utils import timezone


class GoalSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    father_space = serializers.PrimaryKeyRelatedField(queryset=Space.objects.all(), required=False)
    collected = serializers.IntegerField(read_only=True)
    collected_percentage = serializers.SerializerMethodField()
    created_date = serializers.SerializerMethodField()
    created_time = serializers.SerializerMethodField()
    goal_converted = serializers.SerializerMethodField()
    collected_converted = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()

    class Meta:
        model = Goal
        fields = ('id', 'title', 'goal', 'goal_converted', 'collected', 'collected_converted',
                  'father_space', 'collected_percentage', 'currency', 'created_date', 'created_time')

    @staticmethod
    def get_collected_percentage(obj):
        return f"{round(obj.collected_percentage, 2)}%"

    @staticmethod
    def get_goal_converted(obj):
        return convert_number_to_letter(float(obj.goal))

    @staticmethod
    def get_collected_converted(obj):
        return convert_number_to_letter(float(obj.collected))

    def get_created_date(self, obj):
        user_timezone = timezone.get_current_timezone()
        localized_time = obj.created.astimezone(user_timezone)
        return localized_time.strftime('%d %B %Y')

    def get_created_time(self, obj):
        user_timezone = timezone.get_current_timezone()
        localized_time = obj.created.astimezone(user_timezone)
        return localized_time.strftime('%H:%M')

    @staticmethod
    def get_currency(obj):
        return obj.father_space.currency
