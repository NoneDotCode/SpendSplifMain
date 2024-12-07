from django.urls import path
from backend.apps.adminpanel.views import ProjectOverviewView

urlpatterns = [
    path('project_overview/', ProjectOverviewView.as_view(), name='project_overview'),
]