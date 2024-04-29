from rest_framework.generics import get_object_or_404
from rest_framework import generics

from backend.apps.goal.serializers import GoalSerializer
from backend.apps.goal.models import Goal
from backend.apps.goal.permissions import CanCreateGoals, CanEditGoals, CanDeleteGoals

from backend.apps.account.permissions import IsSpaceMember, IsSpaceOwner

from backend.apps.space.models import Space


class CreateGoal(generics.CreateAPIView):
    serializer_class = GoalSerializer
    permission_classes = (IsSpaceMember & (IsSpaceOwner | CanCreateGoals),)

    def get_queryset(self):
        return Goal.objects.filter(father_space_id=self.kwargs.get('space_pk'))

    def create(self, request, *args, **kwargs):
        space_pk = self.kwargs.get('space_pk')
        space = get_object_or_404(Space, pk=space_pk)
        request.data['father_space'] = space.pk
        request.data['collected'] = 0
        return super().create(request, *args, **kwargs)


class EditGoal(generics.RetrieveUpdateAPIView):
    serializer_class = GoalSerializer
    permission_classes = (IsSpaceMember, CanEditGoals)

    def get_queryset(self):
        return Goal.objects.filter(pk=self.kwargs.get('pk'))


class ViewGoals(generics.ListAPIView):
    serializer_class = GoalSerializer
    permission_classes = (IsSpaceMember,)

    def get_queryset(self):
        return Goal.objects.filter(father_space_id=self.kwargs.get('space_pk'))


class DeleteGoal(generics.RetrieveDestroyAPIView):
    serializer_class = GoalSerializer
    permission_classes = (IsSpaceMember, CanDeleteGoals)

    def get_queryset(self):
        return Goal.objects.filter(pk=self.kwargs.get("pk"))
