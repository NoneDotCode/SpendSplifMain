from rest_framework import serializers

from backend.apps.category.models import Category

from backend.apps.space.models import Space


class CategorySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    father_space = serializers.PrimaryKeyRelatedField(queryset=Space.objects.all(), required=False)
    order = serializers.IntegerField(required=False)
    spent = serializers.IntegerField(required=False)
    icon = serializers.CharField(required=False)

    class Meta:
        model = Category
        fields = ('id', 'title', 'spent', 'limit', 'color', 'icon', 'order', 'father_space')
