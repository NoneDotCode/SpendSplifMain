from django.urls import path

from apps.goal.views import CreateGoal, EditGoal, ViewGoals, DeleteGoal

urlpatterns = [
    path('create_goal/', CreateGoal.as_view(), name='create_goal'),
    path('my_goals/', ViewGoals.as_view(), name='view_goals'),
    path('my_goals/<int:pk>/', EditGoal.as_view(), name='edit_goal'),
    path('delete_goal/<int:pk>/', DeleteGoal.as_view(), name='delete_goal')
]
