from rest_framework import permissions

from apps.account.models import Account

from apps.goal.models import Goal

from apps.space.models import Space


class TransferToGoalPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        space_pk = view.kwargs.get("space_pk")
        account_pk = request.data.get("account_pk")
        goal_pk = view.kwargs.get("goal_pk")
        try:
            if Account.objects.get(pk=account_pk).father_space_id != space_pk:
                return False
            if Account.objects.get(pk=account_pk).father_space_id != Goal.objects.get(pk=goal_pk).father_space_id:
                return False
            if Account.objects.get(pk=account_pk).father_space.owner != user:
                return False
        except (Account.DoesNotExist, Goal.DoesNotExist, Space.DoesNotExist):
            return False
        return True
