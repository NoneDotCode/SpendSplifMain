from django.db import transaction
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.reverse import reverse_lazy
from rest_framework.utils import json
from rest_framework import generics, status

from apps.goal.serializers import GoalSerializer
from apps.goal.models import Goal
from apps.goal.permissions import TransferToGoalPermission

from apps.account.models import Account

from apps.converter.utils import convert_currencies

from apps.account.permissions import IsOwnerOfSpace, IsInRightSpace

from apps.space.models import Space

from apps.total_balance.models import TotalBalance


class CreateGoal(generics.CreateAPIView):
    serializer_class = GoalSerializer
    permission_classes = (IsOwnerOfSpace,)

    def get_queryset(self):
        return Goal.objects.filter(father_space_id=self.kwargs.get('space_pk'))

    def create(self, request, *args, **kwargs):
        space_pk = self.kwargs.get('space_pk')
        space = get_object_or_404(Space, pk=space_pk)
        request.data['father_space'] = space.pk
        request.data['spent'] = 0
        return super().create(request, *args, **kwargs)


class EditGoal(generics.RetrieveUpdateAPIView):
    serializer_class = GoalSerializer
    permission_classes = (IsOwnerOfSpace, IsInRightSpace)

    def get_queryset(self):
        return Goal.objects.filter(pk=self.kwargs.get('pk'))


class ViewGoals(generics.ListAPIView):
    serializer_class = GoalSerializer
    permission_classes = (IsOwnerOfSpace,)

    def get_queryset(self):
        return Goal.objects.filter(father_space_id=self.kwargs.get('space_pk'))


class DeleteGoal(generics.RetrieveDestroyAPIView):
    serializer_class = GoalSerializer
    permission_classes = (IsOwnerOfSpace, IsInRightSpace)

    def get_queryset(self):
        return Goal.objects.filter(pk=self.kwargs.get("pk"))
