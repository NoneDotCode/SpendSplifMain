from rest_framework import serializers

from backend.apps.community.models import Post

class PostCreateingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("title", "text", "country")

class PostListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = "__all__"
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        if len(representation['text']) > 50:
            representation['text'] = representation['text'][:50] + '...'  # зріз + '...'
        return representation

class PostDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = "__all__"
    