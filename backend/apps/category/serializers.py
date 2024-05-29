from rest_framework import serializers

from backend.apps.category.models import Category

from backend.apps.space.models import Space


class CategorySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    father_space = serializers.PrimaryKeyRelatedField(queryset=Space.objects.all(), required=False)
    order = serializers.IntegerField(required=False)
    spent = serializers.IntegerField(required=False)
    icon = serializers.CharField(required=False)
    spent_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'title', 'spent', 'limit', 'color', 'icon', 'order', 'father_space', 'spent_percentage')

    @staticmethod
    def get_spent_percentage(obj):
        if obj.limit and obj.spent is not None:
            return f"{round((obj.spent / obj.limit) * 100)}%"
        return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['spent_percentage'] = self.get_spent_percentage(instance)
        return representation
