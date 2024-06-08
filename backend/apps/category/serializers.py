from rest_framework import serializers

from backend.apps.category.models import Category
from backend.apps.space.models import Space
from backend.apps.converter.utils import convert_number_to_letter


class CategorySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    father_space = serializers.PrimaryKeyRelatedField(queryset=Space.objects.all(), required=False)
    spent = serializers.IntegerField(required=False)
    limit = serializers.IntegerField(required=False)
    icon = serializers.CharField(required=False)
    spent_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'title', 'spent', 'limit', 'color', 'icon', 'father_space', 'spent_percentage')

    @staticmethod
    def get_spent_percentage(obj):
        if obj.limit and obj.spent is not None:
            return f"{round((obj.spent / obj.limit) * 100)}%"
        return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['spent_percentage'] = self.get_spent_percentage(instance)

        if representation['spent']:
            representation['spent'] = convert_number_to_letter(representation['spent'])
        if representation['limit']:
            representation['limit'] = convert_number_to_letter(representation['limit'])

        return representation
