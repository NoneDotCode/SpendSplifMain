from rest_framework import permissions

from apps.account.models import Account

from apps.category.models import Category

from apps.space.models import Space


class IsMemberAndCanCreateCategoriesOrOwner(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        space_pk = view.kwargs.get("space_pk")
        try:
            space = Space.objects.get(pk=space_pk)
        except (Space.DoesNotExist,):
            return False

        return ((user in space.members.all()) and
                (space.members.filter(id=user.id, memberpermissions__create_categories=True).exists() or
                 space.members.filter(id=user.id, memberpermissions__owner=True).exists()))


class IsMemberAndCanEditCategoriesOrOwner(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        space_pk = view.kwargs.get("space_pk")
        account_pk = view.kwargs.get("pk")
        try:
            account = Account.objects.get(pk=account_pk)
            space = Space.objects.get(pk=space_pk)
        except (Space.DoesNotExist, Account.DoesNotExist):
            return False

        if account.father_space_id != space_pk:
            return False

        return ((user in space.members.all()) and
                (space.members.filter(id=user.id, memberpermissions__edit_categories=True).exists() or
                 space.members.filter(id=user.id, memberpermissions__owner=True).exists()))


class IsMemberAndCanDeleteCategoriesOrOwner(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user
        space_pk = view.kwargs.get("space_pk")
        account_pk = view.kwargs.get("pk")
        try:
            account = Account.objects.get(pk=account_pk)
            space = Space.objects.get(pk=space_pk)
        except (Space.DoesNotExist, Account.DoesNotExist):
            return False

        if account.father_space_id != space_pk:
            return False

        return ((user in space.members.all()) and
                (space.members.filter(id=user.id, memberpermissions__delete_categories=True).exists() or
                 space.members.filter(id=user.id, memberpermissions__owner=True).exists()))
