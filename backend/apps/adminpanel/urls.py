from django.urls import path
from apps.adminpanel.views import ProjectOverviewView

urlpatterns = [
    path('my_spaces/<str:space_id>/project_overview/', ProjectOverviewView.as_view(), name='project_overview'),
]