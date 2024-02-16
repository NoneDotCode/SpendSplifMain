from rest_framework.permissions import BasePermission

from backend.apps.space.models import Space

from backend.apps.account.models import Account


class IsSpaceMember(BasePermission):

    def has_permission(self, request, view):

        try:
            space = Space.objects.get(pk=view.kwargs.get("space_pk", ))
        except Space.DoesNotExist:
            return False

        if request.user not in space.members.all():
            return False

        return True


class IsSpaceOwner(BasePermission):

    def has_permission(self, request, view):
        space = Space.objects.get(pk=view.kwargs.get("space_pk", ))

        if not space.memberpermissions_set.filter(member=request.user, owner=True).exists():
            return False

        return True


class CanCreateAccounts(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        space_pk = view.kwargs.get("space_pk", )
        space = Space.objects.get(pk=space_pk)

        return space.members.filter(id=user.id, memberpermissions__create_accounts=True).exists()


class CanEditAccounts(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        space_pk = view.kwargs.get("space_pk", )
        account_pk = view.kwargs.get("pk", )
        space = Space.objects.get(pk=space_pk)

        try:
            account = Account.objects.get(pk=account_pk)
        except Account.DoesNotExist:
            return False

        if account.father_space_id != space_pk:
            return False

        return (IsSpaceOwner().has_permission(request, view) or
                space.members.filter(id=user.id, memberpermissions__edit_accounts=True).exists())


class CanDeleteAccounts(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        space_pk = view.kwargs.get("space_pk", )
        account_pk = view.kwargs.get("pk", )
        space = Space.objects.get(pk=space_pk)

        try:
            account = Account.objects.get(pk=account_pk)
        except Account.DoesNotExist:
            return False

        if account.father_space_id != space_pk:
            return False

        return (IsSpaceOwner().has_permission(request, view) or
                space.members.filter(id=user.id, memberpermissions__delete_accounts=True).exists())


class IncomePermission(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        space_pk = view.kwargs.get('space_pk', )
        account_pk = view.kwargs.get('pk', )
        space = Space.objects.get(pk=space_pk)

        try:
            account = Account.objects.get(pk=account_pk)
        except Account.DoesNotExist:
            return False

        if account.father_space != space:
            return False

        return (IsSpaceOwner().has_permission(request, view) or
                space.members.filter(id=user.id, memberpermissions__income=True).exists())
