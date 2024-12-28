from rest_framework import serializers
from backend.apps.adminpanel.models import ProjectOverview

class ProjectOverviewSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
    data = serializers.DecimalField(max_digits=10, decimal_places=0, coerce_to_string=False)

    class Meta:
        model = ProjectOverview
        fields = '__all__'
