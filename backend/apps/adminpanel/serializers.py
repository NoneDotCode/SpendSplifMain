from rest_framework import serializers
from backend.apps.adminpanel.models import ProjectOverview

class ProjectOverviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectOverview
        fields = ['space', 'assets', 'data', 'price', 'updated_date']