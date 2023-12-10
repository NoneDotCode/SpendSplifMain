from rest_framework import serializers

from apps.category.models import Category

from apps.space.models import Space


class CategorySerializer(serializers.ModelSerializer):
    father_space = serializers.PrimaryKeyRelatedField(queryset=Space.objects.all(), required=False)

    class Meta:
        model = Category
        fields = ('title', 'spent', 'limit', 'father_space')
