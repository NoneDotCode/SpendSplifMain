from rest_framework import serializers

from apps.goal.models import Goal


class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = ('title', 'goal', 'collected', 'father_space', 'created')
