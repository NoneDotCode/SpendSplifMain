from rest_framework import serializers
from apps.adminpanel.models import ProjectOverview

class ProjectOverviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectOverview
        fields = ['space', 'assets', 'data', 'price', 'updated_date']