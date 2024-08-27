from rest_framework import serializers
from .models import Banner

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ['id', 'image', 'views', 'clicks', 'created_at', 'is_active', 'goal_view', 'goal_click', 'link', 'owner']