from django.urls import path
from backend.apps.adminpanel.views import ProjectOverviewView, TotalDeposits, ServiceStatistic

urlpatterns = [
    path('project_overview/', ProjectOverviewView.as_view(), name='project_overview'),
    path('total_deposits/', TotalDeposits.as_view(), name='project_overview'),
    path('service_statistic/', ServiceStatistic.as_view(), name='project_overview'),
]