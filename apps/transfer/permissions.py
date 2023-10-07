from rest_framework import permissions

from apps.space.models import Space

from apps.account.models import Account

from apps.goal.models import Goal


class TransferPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        from_object = request.data.get("from_object")
        to_object = request.data.get("to_object")
        try:
            if from_object == "goal" and to_object == "goal":
                return True
            elif from_object == "goal" and to_object == "account":
                space = Space.objects.get(pk=view.kwargs.get("space_pk"))
                goal = Goal.objects.get(pk=request.data.get("from_goal"))
                account = Account.objects.get(pk=request.data.get("to_account"))
                return space.owner == request.user and goal.father_space == space and account.father_space == space
            elif from_object == "account" and to_object == "goal":
                space = Space.objects.get(pk=view.kwargs.get("space_pk"))
                goal = Goal.objects.get(pk=request.data.get("to_goal"))
                account = Account.objects.get(pk=request.data.get("from_account"))
                return space.owner == request.user and goal.father_space == space and account.father_space == space
            elif from_object == "account" and to_object == "account":
                space = Space.objects.get(pk=view.kwargs.get("space_pk"))
                from_account = Account.objects.get(request.data.get("from_account"))
                to_account = Account.objects.get(request.data.get("to_account"))
                return space.owner == request.user and from_account.father_space == space and \
                    to_account.father_space == space
        except (Account.DoesNotExist, Space.DoesNotExist, Goal.DoesNotExist):
            return False
