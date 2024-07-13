from rest_framework import permissions

from backend.apps.account.models import Account
from backend.apps.account.permissions import IsSpaceOwner

from backend.apps.goal.models import Goal

from backend.apps.space.models import Space


class CanCreateGoals(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        space_pk = view.kwargs.get("space_pk", )
        space = Space.objects.get(pk=space_pk)

        return space.members.filter(id=user.id, memberpermissions__create_goals=True).exists()


class CanEditGoals(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        space_pk = view.kwargs.get("space_pk", )
        goal_pk = view.kwargs.get("pk", )
        space = Space.objects.get(pk=space_pk)

        try:
            goal = Goal.objects.get(pk=goal_pk)
        except Goal.DoesNotExist:
            return False

        if goal.father_space_id != space_pk:
            return False

        return (IsSpaceOwner().has_permission(request, view) or
                space.members.filter(id=user.id, memberpermissions__edit_goals=True).exists())


class CanDeleteGoals(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        space_pk = view.kwargs.get("space_pk")
        goal_pk = view.kwargs.get("pk")
        space = Space.objects.get(pk=space_pk)

        try:
            goal = Goal.objects.get(pk=goal_pk)
        except Goal.DoesNotExist:
            return False

        if goal.father_space_id != space_pk:
            return False

        return ((IsSpaceOwner().has_permission(request, view)) or
                (space.members.filter(id=user.id, memberpermissions__delete_goals=True).exists()))
